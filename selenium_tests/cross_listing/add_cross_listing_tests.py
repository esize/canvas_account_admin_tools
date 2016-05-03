from ddt import ddt, data, unpack

from selenium_common.base_test_case import get_xl_data

from selenium_tests.cross_listing.cross_listing_base_test_case import \
    CrossListingBaseTestCase, TEST_DATA_CROSS_LISTING_MAPPINGS

@ddt
class AddCrossListingTests(CrossListingBaseTestCase):

    @data(*get_xl_data(TEST_DATA_CROSS_LISTING_MAPPINGS))
    @unpack
    def test_add_cross_listing_pairing(self, test_case,
                                       primary_cid,
                                       secondary_cid,
                                       expected_result):

        """
        TLT-2589, AC #1 and 7
        This test adds a valid cross-list pairing to the cross-listing table
        """
        # This adds the pairing to the cross-list table and clicks submit
        self.main_page.add_cross_listing_pairing(primary_cid, secondary_cid)

        # This verifies that the confirmation box appears
        self.assertTrue(
                self.main_page.confirm_presence_of_confirmation_alert()
        )

        #  Verifies a successful cross-list add
        if expected_result == 'success':
            expected_text = "{} was successfully crosslisted with {}.".format(
                primary_cid, secondary_cid)
            actual_text = self.main_page.get_confirmation_text()
            # Verifies that the expected success message matches the actual
            # success confirmation message
            self.assertEqual(actual_text, expected_text,
                             "Error. Expected success message is '{}' but "
                             "message is returning '{}'".format(expected_text,
                                                                actual_text))


        # Verifies error message if cross-listing is unsuccessful
        if expected_result == 'fail':
            expected_text = 'could not be crosslisted'
            actual_text = self.index_page.get_confirmation_text()
            self.assertEqual(actual_text, expected_text,
                             "Error. Expected error is '{}' but error is "
                             "returning '{}'".format(expected_text,
                                                     actual_text))

        #  Verifies test_data spreadsheet contains a value in the "expected
        #  result" column
        else:
            raise ValueError('given_access column for expected result {} must '
                             'be either '
                             '\'fail\' or \'success\''.format(expected_result))

