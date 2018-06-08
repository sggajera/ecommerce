from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from accounts.models import GuestEmail
import braintree

User = settings.AUTH_USER_MODEL



# abc@teamcfe.com -->> 1000000 billing profiles
# user abc@teamcfe.com -- 1 billing profile
if settings.DEBUG:
	gateway = braintree.BraintreeGateway(
	  braintree.Configuration(
		braintree.Environment.Sandbox,
		merchant_id='k3kvjjk63tgvjjhb',
		public_key='bmtfyhvfjgg7dd97',
		private_key='d104b15a2e0150dd8881d156aa097ce9'
	  )
	)

class BillingProfileManager(models.Manager):
	def new_or_get(self, request):
		user = request.user
		guest_email_id = request.session.get('guest_email_id')
		created = False
		obj = None
		if user.is_authenticated():
			'logged in user checkout; remember payment stuff'

			obj, created = self.model.objects.get_or_create(
							user=user, email=user.email)
		elif guest_email_id is not None:
			'guest user checkout; auto reloads payment stuff'
			guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
			obj, created = self.model.objects.get_or_create(
											email=guest_email_obj.email)
		else:
			pass
		return obj, created
	

class BillingProfile(models.Model):
	user        = models.OneToOneField(User, null=True, blank=True)
	email       = models.EmailField()
	active      = models.BooleanField(default=True)
	update      = models.DateTimeField(auto_now=True)
	timestamp   = models.DateTimeField(auto_now_add=True)
	braintree_id = models.CharField(max_length=120, null=True,blank=True)
	
	objects= BillingProfileManager()

	def __str__(self):
		return self.email

	@property
	def get_braintree_id(self):
		instance = self
		if not instance.braintree_id:
			result = gateway.customer.create({
				"email" : instance.email
			})
			if result.is_success:
				instance.braintree_id = result.customer.id
				instance.save()

	def get_client_token(self):
		customer_id = self.get_braintree_id
		# if customer_id:
		client_token = gateway.client_token.generate({
			    "customer_id": customer_id
			})
		return client_token
		


def update_braintree_id(sender, instance, *args, **kwargs):
	if not instance.braintree_id:
		instance.get_braintree_id
		
		#update
		

post_save.connect(update_braintree_id,sender= BillingProfile)


def user_created_receiver(sender, instance, created, *args, **kwargs):
	if created and instance.email:
		BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_receiver, sender=User)