from factory.fuzzy import FuzzyText
import io
from unittest.mock import patch

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase

from . import factories


class TestOptimizedImageField(TestCase):
    """Test case for the OptimizedImageField."""

    @patch('optimized_image.utils.optimize_from_buffer')
    def test_save_does_not_create_optimized_image(self, mock_optimize_from_buffer):
        """Saving an image to an OptimizedImageField does not call optimize_from_buffer()."""
        generic_model = factories.GenericModelFactory(
            title='Generic Model',
            image=None
        )
        # So far there is no optimized image, and mock_optimize_from_buffer has not been called
        self.assertEqual(generic_model.image.name, None)
        self.assertEqual(mock_optimize_from_buffer.call_count, 0)

        new_io = io.StringIO()
        new_io.write('something')
        new_file = InMemoryUploadedFile(
            new_io,
            'image',
            'static/images/{}.png'.format(FuzzyText().fuzz()),
            'image/jpeg',
            len(new_io.getvalue()),
            'utf-8'
        )
        generic_model.image = new_file
        generic_model.save()

        self.assertNotEqual(generic_model.image.name, None)
        # The mock_optimize_from_buffer still has not been called
        self.assertEqual(mock_optimize_from_buffer.call_count, 0)

    @patch('optimized_image.utils.optimize_from_buffer')
    def test_save_form_data(self, mock_optimize_from_buffer):
        """Calling save_form_data() on an OptimizedImageField calls optimize_from_buffer()."""
        generic_model = factories.GenericModelFactory(
            title='Generic Model',
            image=None
        )
        # So far there is no optimized image, and mock_optimize_from_buffer has not been called
        self.assertEqual(generic_model.image.name, None)
        self.assertEqual(mock_optimize_from_buffer.call_count, 0)

        new_io = io.StringIO()
        new_io.write('something')
        new_file = InMemoryUploadedFile(
            new_io,
            'image',
            'static/images/{}.png'.format(FuzzyText().fuzz()),
            'image/jpeg',
            len(new_io.getvalue()),
            'utf-8'
        )

        # Call save_form_data on the OptimizedImageField
        generic_model.image.field.save_form_data(generic_model, new_file)

        # Now the mock_optimize_from_buffer has been called once
        self.assertEqual(mock_optimize_from_buffer.call_count, 1)
        self.assertEqual(mock_optimize_from_buffer.call_args[0][0], new_file)
