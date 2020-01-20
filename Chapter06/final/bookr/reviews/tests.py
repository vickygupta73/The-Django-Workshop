import re
from unittest import mock

from django.http import HttpRequest, QueryDict
from django.test import Client
from django.test import TestCase

from reviews.forms import PublisherForm
from reviews.models import Publisher
from reviews.views import publisher_edit


class Exercise10Test(TestCase):
    def test_fields_in_view(self):
        """"
        Test that fields exist in the rendered template.
        """
        c = Client()
        response = c.get('/publishers/new/')

        self.assertIsNotNone(re.search(r'<input type="hidden" name="csrfmiddlewaretoken" value="\w+">',
                                       response.content.decode('ascii')))

        self.assertIn(
            b'<label for="id_name">Name:</label> <input type="text" name="name" maxlength="50" required id="id_name"> '
            b'<span class="helptext">The name of the Publisher.</span></p>',
            response.content)
        self.assertIn(
            b'<label for="id_website">Website:</label> <input type="url" name="website" maxlength="200" '
            b'required id="id_website"> <span class="helptext">The Publisher\'s website.</span></p>',
            response.content)
        self.assertIn(
            b'<label for="id_email">Email:</label> <input type="email" name="email" maxlength="254" '
            b'required id="id_email"> <span class="helptext">The Publisher\'s email address.</span>',
            response.content)
        self.assertIn(b'<input type="submit" name="submit_input" value="Submit Input">', response.content)
        self.assertIn(b'<button type="submit" name="button_element" value="Button Element">', response.content)
        self.assertIn(b'Button With <strong>Styled</strong> Text', response.content)
        self.assertIn(b'</button>', response.content)

    def test_method_in_view(self):
        """Test that the method is included in the HTML output"""
        c = Client()
        response = c.get('/publishers/new/')
        self.assertIn(b'<h4>Method: GET</h4>', response.content)

        response = c.post('/publishers/new/')
        self.assertIn(b'<h4>Method: POST</h4>', response.content)

    def test_publisher_create(self):
        """Test the creation of a new Publisher"""
        self.assertEqual(Publisher.objects.all().count(), 0)
        c = Client()
        publisher_name = 'Test Create Publisher'
        publisher_website = 'http://www.example.com/test-publisher/'
        publisher_email = 'test-publisher@example.com'

        response = c.post('/publishers/new/', {
            'name': publisher_name,
            'website': publisher_website,
            'email': publisher_email
        })
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Publisher.objects.all().count(), 1)
        publisher = Publisher.objects.first()
        self.assertEqual(publisher.name, publisher_name)
        self.assertEqual(publisher.website, publisher_website)
        self.assertEqual(publisher.email, publisher_email)
        self.assertEqual(response['Location'], '/publishers/{}/'.format(publisher.pk))

    def test_publisher_no_create(self):
        """Test that no Publisher is created if the form is invalid."""
        self.assertEqual(Publisher.objects.all().count(), 0)
        c = Client()

        response = c.post('/publishers/new/', {
            'name': '',
            'website': 'not a url',
            'email': 'not an email'
        })
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Publisher.objects.all().count(), 0)

    def test_publisher_edit(self):
        """
        Test editing a publisher, the initial GET should have a form with values and then the post should update the
        Publisher rather than creating a new one.
        """
        publisher_name = 'Test Edit Publisher'
        publisher_website = 'http://www.example.com/edit-publisher/'
        publisher_email = 'edit-publisher@example.com'
        publisher = Publisher(name=publisher_name, website=publisher_website, email=publisher_email)
        publisher.save()
        self.assertEqual(Publisher.objects.all().count(), 1)

        c = Client()

        response = c.get('/publishers/{}/'.format(publisher.pk))

        self.assertIn(b'value="Test Edit Publisher"', response.content)
        self.assertIn(b'value="http://www.example.com/edit-publisher/"', response.content)
        self.assertIn(b'value="edit-publisher@example.com"', response.content)

        response = c.post('/publishers/{}/'.format(publisher.pk), {
            'name': 'Updated Name',
            'website': 'https://www.example.com/updated/',
            'email': 'updated@example.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Publisher.objects.all().count(), 1)
        publisher2 = Publisher.objects.first()

        self.assertEqual(publisher2.pk, publisher.pk)
        self.assertEqual(publisher2.name, 'Updated Name')
        self.assertEqual(publisher2.website, 'https://www.example.com/updated/')
        self.assertEqual(publisher2.email, 'updated@example.com')
