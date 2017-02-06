from django.test import TestCase
from channels import Channel
from channels.tests import ChannelTestCase
from django.contrib.auth.models import User
from .consumers import msg_consumer
from .forms import RegistrationForm
from .models import Message, Room


class ConsumerTestCase(ChannelTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name="petter",
            last_name="castro",
            username='petter',
            email='petter@gmail.com',
            password='top_secret'
        )
        self.user2 = User.objects.create_user(
            first_name="luis",
            last_name="salazar",
            username='lsalazar',
            email='luis@gmail.com',
            password='d2ming'
        )

        self.room = Room.objects.create(label="123456789")
        self.room.subscribers.add(self.user)
        self.room.subscribers.add(self.user2)

        self.client.post('/login/', {'username': 'petter', 'password': 'top_secret'})  

    def test_ws_days(self):
        data = {
            "message": "/YQL|DaysLow,DaysHigh=AAPL",
            "username": "lsalazar",
            "room": "123456789"
        }
        Channel(u"chatmessages").send(data)
        tr = self.get_next_message(u"chatmessages")
        response = msg_consumer(tr)
        self.assertTrue("APPL (apple INC) Days Low quote is $" in response['message'])


    def test_ws_stock(self):
        data = {
            "message": "/FNC|price=AAPL",
            "username": "lsalazar",
            "room": "123456789"
        }
        Channel(u"chatmessages").send(data)
        tr = self.get_next_message(u"chatmessages")
        response = msg_consumer(tr)
        self.assertTrue('APPL (apple INC) quote is $' in response['message'])


    def test_ws_stock_missing_params(self):
        data = {
            "message": "/FNC|priceDD=AAPL",
            "username": "lsalazar",
            "room": "123456789"
        }
        Channel(u"chatmessages").send(data)
        tr = self.get_next_message(u"chatmessages")
        response = msg_consumer(tr)
        self.assertTrue("No enough arguments" in response['message'])

    def test_ws_stock_another_company(self):
        data = {
            "message": "/FNC|price=GOOGL",
            "username": "lsalazar",
            "room": "123456789"
        }
        Channel(u"chatmessages").send(data)
        tr = self.get_next_message(u"chatmessages")
        response = msg_consumer(tr)
        self.assertTrue('APPL (apple INC) quote is $' in response['message'])


class RegistrationTestCase(TestCase):
    def test_registration_create_form(self):
        form_data = {
            'username': 'pcastro', 
            'first_name': 'Petter', 
            'last_name': 'Castro', 
            'email': 'pcastro@gmail.com', 
            'password1': '123demn3', 
            'password2': '123demn3'
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_create_form_blank_data(self):
        form_data = {
            'username': '', 
            'first_name': 'Petter', 
            'last_name': 'Castro', 
            'email': 'pcastro@gmail.com', 
            'password1': '123demn3', 
            'password2': '123demn3'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_registration_create_form_invalid_data(self):
        form_data = {
            'username': '',
            'first_name': 'Petter',
            'last_name': 'Castro',
            'email': 'pcastrogmail.com',
            'password1': '123demn3',
            'password2': '123demn3'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_registration_create_form_existing_user(self):
        form_data = {
            'username': 'pcastro',
            'first_name': 'Petter',
            'last_name': 'Castro',
            'email': 'pcastro@gmail.com',
            'password1': '123demn3',
            'password2': '123demn3'
        }
        self.client.post("/register/", form_data)

        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())


class ChatTestCase(ChannelTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name="petter",
            last_name="castro",
            username='petter',
            email='petter@gmail.com',
            password='top_secret'
        )
        self.user2 = User.objects.create_user(
            first_name="luis",
            last_name="salazar",
            username='lsalazar',
            email='luis@gmail.com',
            password='d2ming'
        )

        self.room = Room.objects.create(label="123456789")
        self.room.subscribers.add(self.user)
        self.room.subscribers.add(self.user2)

        self.client.post('/login/', {'username': 'petter', 'password': 'top_secret'})  

    def test_chat_create(self):
        data = {
            "message": "This is my msg",
            "username": "lsalazar",
            "room": "123456789"
        }
        Channel(u"chatmessages").send(data)
        tr = self.get_next_message(u"chatmessages")
        self.assertEqual(tr['message'], data["message"])

        msg_consumer(tr)
        num = Message.objects.filter(message=data["message"]).count()
        self.assertEqual(num, 1)

    def test_chat_set_days_appl_not_in_db(self):
        data = {
            "message": "/YQL|DaysLow,DaysHigh=AAPL",
            "username": "lsalazar",
            "room": "123456789"
        }
        Channel(u"chatmessages").send(data)
        tr = self.get_next_message(u"chatmessages")

        msg_consumer(tr)
        num = Message.objects.filter(message=data["message"]).count()
        self.assertEqual(num, 0)

    def test_chat_set_stock_appl_not_in_db(self):
        data = {
            "message": "/YQL|price=AAPL",
            "username": "lsalazar",
            "room": "123456789"
        }
        Channel(u"chatmessages").send(data)
        tr = self.get_next_message(u"chatmessages")

        msg_consumer(tr)
        num = Message.objects.filter(message=data["message"]).count()
        self.assertEqual(num, 0)
