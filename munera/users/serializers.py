from rest_framework import serializers

from users.models import User
from users.services import create_user as create_user_service, authenticate_user


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=30)
    email = serializers.EmailField(max_length=60)
    password = serializers.CharField(write_only=True, max_length=256)
    password_confirm = serializers.CharField(write_only=True, max_length=256)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "alias",
            "email",
            "username",
            "password",
            "password_confirm",
        )

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.pop("password_confirm", None)

        if password_confirm is None:
            raise serializers.ValidationError({"password_confirm": "This field is required."})

        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})

        if password and len(password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters."})
        
        username = attrs.get("username")
        email = attrs.get("email")

        if User.objects.filter(user_name=username).exists():
            raise serializers.ValidationError({"username": "Username is already taken."})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email is already registered."})

        return attrs

    def create(self, validated_data):
        user = create_user_service(
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            email=validated_data.get("email"),
            username=validated_data.get("username"),
            password=validated_data.get("password"),
            alias=validated_data.get("alias"),
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True, max_length=256)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")
        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")

        user = authenticate_user(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        attrs["user"] = user
        return attrs
