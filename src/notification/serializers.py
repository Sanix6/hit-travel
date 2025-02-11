from rest_framework import serializers

from .models import TokenFCM, UserToken


class TokenCreateSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=True)

    class Meta:
        model = UserToken
        fields = ("token",)

    def create(self, validated_data):
        token = TokenFCM.objects.get_or_create(token=validated_data.get("token"))[0]
        user = self.context["request"].user
        user_token = user.tokens.order_by("-created_at").last()
        if user_token is None or not user_token.is_active:
            return UserToken.objects.create(user=user, token=token)
        return user_token
