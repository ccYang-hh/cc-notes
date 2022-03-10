from rest_framework import serializers

from cc_notes.utils.serializers import Base64ImageField
from .models import Article, Archive
from users.serializers import SimpleUserSerializer, SimpleArticleSerializer
from taggit.serializers import (TagListSerializerField, TaggitSerializer)


class ArchiveSerializer(serializers.ModelSerializer):
    author = SimpleUserSerializer(read_only=True)
    articles = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Archive
        fields = ['id', 'name', 'author', 'articles', 'created', 'isPublic']

    def create(self, validated_data):
        request = self.context['request']
        archive = Archive(**validated_data)
        archive.author = request.user
        archive.save()
        return archive

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.isPublic = validated_data.get('isPublic', instance.isPublic)
        instance.save()
        return instance


class ArchiveSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archive
        fields = ['id', 'name', 'created', 'isPublic']


"""
article部分的全部序列化器
"""


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'total_views']


"""
重写序列化article时，article的comments字段，由于是外键字段，因此重写需继承RelatedField
重写to_representation(self, value)方法以实现只序列化article的根评论

一开始的考虑：只序列化根评论，然后由前端请求子评论，这样做可以让article的序列化数据大大减少
第二版考虑：既然无论如何都要请求子评论，那么不如现在就全部请求过来，也方便统一展示
优缺点：现在的考虑更适合个人项目，因为文章评论并不太多，就算全部请求过来也不会有太明显的延时
       如果是大型项目，评论数据很多，那么可以后续异步请求时获得

第三版考虑：将comments和article独立开来，分别请求，这样也能更容易的在视图层筛选根评论，而不是在序列化层筛选
            比如设计一个api：article-comments/<int:article_id>/ 代表该id的article的所有评论
            设计一个api：article-comments/root/<int:article_id>/ 代表该id的article的所有根评论
经过代码的编写，最终确定第三版考虑要更加合理
"""


# class CommentsListField(serializers.RelatedField):
#
#     def to_representation(self, value):
#         if not value.parent:
#             return ChildrenCommentSerializer(value).data


class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    """
    article的序列化器，不需要序列化评论
    """
    tags = TagListSerializerField()
    collectors = SimpleUserSerializer(many=True, read_only=True, required=False)
    author = SimpleUserSerializer(read_only=True)
    archive = ArchiveSimpleSerializer(required=False, read_only=True)

    # comments = CommentsListField（many=True,read_only=True)

    class Meta:
        model = Article
        # 尽量不要用__all__来指定fields，因为一旦模型被更改，可能会导致数据泄露
        fields = ['id', 'author', 'title', 'body', 'avatar', 'bodyType', 'created', 'collectors', 'category', 'markdownText',
                  'updated', 'total_views', 'tags', 'supports', 'isPublic', 'isStar', 'isDraft', 'description', 'archive']
        extra_kwargs = {
            # 'url': {
            #     'view_name': 'article-detail'
            # },
            'supports':  {'read_only': True}
        }

    def create(self, validated_data):
        request = self.context['request']
        tags = validated_data['tags']
        del validated_data['tags']
        article = Article(**validated_data)
        article.author = request.user
        for tag in tags:
            article.tags.add(tag)
        article.save()
        return article

    def update(self, instance, validated_data):
        instance.tags.clear()
        for tag in validated_data.get('tags', instance.tags.all()):
            instance.tags.add(tag)
        instance.title = validated_data.get('title', instance.title)
        instance.body = validated_data.get('body', instance.body)
        instance.markdownText = validated_data.get('markdownText', instance.markdownText)
        instance.isStar = validated_data.get('isStar', instance.isStar)
        instance.isDraft = validated_data.get('isDraft', instance.isDraft)
        instance.isPublic = validated_data.get('isPublic', instance.isPublic)
        instance.description = validated_data.get('description', instance.description)
        instance.category = validated_data.get('category', instance.category)
        instance.save()
        return instance


class ArticleAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Article
        fields = ['id', 'avatar']

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance

