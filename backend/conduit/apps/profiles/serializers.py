from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    bio = serializers.CharField(allow_blank=True, required=False)
    image = serializers.CharField(allow_blank=True, required=False)
    following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'bio', 'image', 'following',)
        read_only_fields = ('username',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not representation.get('image'):
            representation['image'] = 'https://i.pravatar.cc/300'
        return representation

    def get_following(self, instance):
        request = self.context.get('request', None)
        if request is None:
            return False
        if not request.user.is_authenticated():
            return False
        follower = request.user.profile
        followee = instance
        return follower.is_following(followee)