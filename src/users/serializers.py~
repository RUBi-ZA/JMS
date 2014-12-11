from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from users.models import *

class CountrySerializer(serializers.ModelSerializer):
	class Meta:
		model = Country


class UserSerializer(serializers.ModelSerializer):	
	class Meta:
		model = get_user_model()
		fields = ('date_joined','email','first_name','id','last_login','last_name','username')
		
class GroupUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = get_user_model()
		fields = ('id','username')

class GroupSerializer(serializers.ModelSerializer):
	user_set = GroupUserSerializer(many=True)
	
	class Meta:
		model = Group
		fields = ('id', 'name', 'user_set')		

class UserProfileSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	Country = CountrySerializer()

	class Meta:
		model = UserProfile

class UserProfileNameSerializer(serializers.ModelSerializer):
	user = UserSerializer()

	class Meta:
		model = UserProfile
		fields = ('user',)

class ContactUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = get_user_model()
		fields = ('date_joined','first_name','id','last_name','username')

class ContactProfileSerializer(serializers.ModelSerializer):
	user = ContactUserSerializer()
	Country = CountrySerializer()
	
	class Meta:
		model = UserProfile

class ContactSerializer(serializers.ModelSerializer):
	ContactProfile = ContactProfileSerializer()
	
	class Meta:
		model = Contact

class MessageSerializer(serializers.ModelSerializer):	
	UserProfile = UserProfileNameSerializer()
	
	class Meta:
		model = Message
		fields = ('MessageID', 'Content', 'Date', 'UserProfile')

class UserConversationSerializer(serializers.ModelSerializer):
	UserProfile = UserProfileSerializer()
	
	class Meta:
		model = UserConversation

class FullConversationSerializer(serializers.ModelSerializer):
	UserConversations = UserConversationSerializer(many=True)
	Messages = MessageSerializer(many=True)
	
	class Meta:
		model = Conversation
		fields = ('ConversationID', 'Subject', 'LastMessage', 'UserConversations', 'Messages')

class ConversationSerializer(serializers.ModelSerializer):
	UserConversations = UserConversationSerializer(many=True)
	
	class Meta:
		model = Conversation
		fields = ('ConversationID', 'Subject', 'LastMessage', 'UserConversations')

class GroupConversationSerializer(serializers.ModelSerializer):
	Conversation = FullConversationSerializer()
	
	class Meta:
		model = GroupConversation
		fields = ('Conversation',)

class GroupDetailSerializer(serializers.ModelSerializer):
	user_set = GroupUserSerializer(many=True)
	groupconversation = GroupConversationSerializer()
	
	class Meta:
		model = Group
		fields = ('id', 'name', 'user_set', 'groupconversation')
