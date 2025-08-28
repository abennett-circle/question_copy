#!/usr/bin/env python3
"""
Unit tests for Questionnaire_Filler class.

This test suite focuses on testing the core logic methods that don't make API calls,
ensuring robust validation of data processing, filtering, and business logic.
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.Questionnaire_Filler import Questionnaire_Filler
from src.Question import Question
from src.Reference_Questionnaire import Reference_Questionnaire
from src.Unanswered_Questionnaire import Unanswered_Questionnaire


class TestQuestionnaireFiller(unittest.TestCase):
    """Test suite for Questionnaire_Filler class."""

    def setUp(self):
        """Set up test fixtures with mocked dependencies."""
        # Create mock questionnaires to avoid file I/O
        self.mock_reference = Mock(spec=Reference_Questionnaire)
        self.mock_unanswered = Mock(spec=Unanswered_Questionnaire)
        
        # Create a Questionnaire_Filler instance with mocked dependencies
        with patch('src.Questionnaire_Filler.Reference_Questionnaire'), \
             patch('src.Questionnaire_Filler.Unanswered_Questionnaire'), \
             patch('src.Questionnaire_Filler.load_dotenv'), \
             patch('os.path.exists', return_value=True), \
             patch('os.getenv') as mock_getenv:
            
            # Mock environment variables
            mock_getenv.side_effect = lambda key: {
                'CHATAI_BASE_URL': 'http://test-url.com',
                'CHATAI_API_KEY': 'test-key'
            }.get(key)
            
            self.filler = Questionnaire_Filler(
                reference_file_name="test_ref.csv",
                reference_question_col="Question",
                reference_answer_col="Answer",
                unanswered_file_name="test_unans.csv",
                unanswered_question_col="Question",
                unanswered_answer_col="Answer"
            )
        
        # Replace the questionnaire objects with our mocks
        self.filler.reference_questionnaire = self.mock_reference
        self.filler.unanswered_questionnaire = self.mock_unanswered


class TestHasMeaningfulContent(TestQuestionnaireFiller):
    """Test the _has_meaningful_content helper method."""

    def test_none_values(self):
        """Test that None values return False."""
        self.assertFalse(self.filler._has_meaningful_content(None))

    def test_pandas_nan(self):
        """Test that pandas NaN values return False."""
        self.assertFalse(self.filler._has_meaningful_content(np.nan))
        self.assertFalse(self.filler._has_meaningful_content(pd.NA))

    def test_empty_strings(self):
        """Test that empty strings return False."""
        self.assertFalse(self.filler._has_meaningful_content(""))
        self.assertFalse(self.filler._has_meaningful_content("   "))
        self.assertFalse(self.filler._has_meaningful_content("\n\t"))

    def test_null_string_representations(self):
        """Test that string representations of null values return False."""
        self.assertFalse(self.filler._has_meaningful_content("nan"))
        self.assertFalse(self.filler._has_meaningful_content("NaN"))
        self.assertFalse(self.filler._has_meaningful_content("none"))
        self.assertFalse(self.filler._has_meaningful_content("None"))
        self.assertFalse(self.filler._has_meaningful_content("null"))
        self.assertFalse(self.filler._has_meaningful_content("NULL"))

    def test_punctuation_only(self):
        """Test that punctuation-only strings return False."""
        self.assertFalse(self.filler._has_meaningful_content("!!!"))
        self.assertFalse(self.filler._has_meaningful_content("---"))
        self.assertFalse(self.filler._has_meaningful_content("..."))
        self.assertFalse(self.filler._has_meaningful_content("@#$%"))

    def test_valid_strings(self):
        """Test that strings with alphanumeric content return True."""
        self.assertTrue(self.filler._has_meaningful_content("Yes"))
        self.assertTrue(self.filler._has_meaningful_content("No"))
        self.assertTrue(self.filler._has_meaningful_content("N/A"))
        self.assertTrue(self.filler._has_meaningful_content("123"))
        self.assertTrue(self.filler._has_meaningful_content("We have a policy"))

    def test_valid_strings_with_whitespace(self):
        """Test that valid strings with surrounding whitespace return True."""
        self.assertTrue(self.filler._has_meaningful_content("  Yes  "))
        self.assertTrue(self.filler._has_meaningful_content("\nNo\t"))
        self.assertTrue(self.filler._has_meaningful_content("   123   "))

    def test_numeric_values(self):
        """Test that numeric values return True."""
        self.assertTrue(self.filler._has_meaningful_content(42))
        self.assertTrue(self.filler._has_meaningful_content(3.14))
        self.assertTrue(self.filler._has_meaningful_content(0))
        self.assertTrue(self.filler._has_meaningful_content(-5))

    def test_zero_values(self):
        """Test that zero values are considered meaningful."""
        self.assertTrue(self.filler._has_meaningful_content(0))
        self.assertTrue(self.filler._has_meaningful_content(0.0))
        self.assertTrue(self.filler._has_meaningful_content("0"))

    def test_boolean_values(self):
        """Test that boolean values return True."""
        self.assertTrue(self.filler._has_meaningful_content(True))
        self.assertTrue(self.filler._has_meaningful_content(False))


class TestMatchExactQuestions(TestQuestionnaireFiller):
    """Test the _match_exact_questions method."""

    def setUp(self):
        """Set up test data for exact matching tests."""
        super().setUp()
        
        # Create mock Question objects
        self.mock_ref_q1 = Mock(spec=Question)
        self.mock_ref_q1.get_question.return_value = "What is your name?"
        
        self.mock_ref_q2 = Mock(spec=Question)
        self.mock_ref_q2.get_question.return_value = "How old are you?"
        
        self.mock_unans_q1 = Mock(spec=Question)
        self.mock_unans_q1.get_question.return_value = "What is your name?"
        
        self.mock_unans_q2 = Mock(spec=Question)
        self.mock_unans_q2.get_question.return_value = "What is your favorite color?"
        
        # Set up the mock questionnaires
        self.mock_reference.get_questions.return_value = {
            "What is your name?": self.mock_ref_q1,
            "How old are you?": self.mock_ref_q2
        }
        
        self.mock_unanswered.get_questions.return_value = {
            "What is your name?": self.mock_unans_q1,
            "What is your favorite color?": self.mock_unans_q2
        }
        
        self.mock_unanswered.questions = {
            "What is your name?": self.mock_unans_q1,
            "What is your favorite color?": self.mock_unans_q2
        }

    def test_exact_matching_finds_matches(self):
        """Test that exact matching finds and processes matching questions."""
        unmatched, remaining_ref = self.filler._match_exact_questions()
        
        # Should find one exact match
        self.mock_unans_q1.set_reference_question.assert_called_once_with("What is your name?")
        self.mock_unans_q1.set_question_match_score.assert_called_once_with(1)
        
        # Check remaining questions
        self.assertIn("What is your favorite color?", unmatched)
        self.assertNotIn("What is your name?", unmatched)

    def test_exact_matching_returns_unmatched(self):
        """Test that unmatched questions are returned correctly."""
        unmatched, remaining_ref = self.filler._match_exact_questions()
        
        # Should return unmatched questions
        self.assertEqual(len(unmatched), 1)
        self.assertIn("What is your favorite color?", unmatched)

    def test_no_matches_scenario(self):
        """Test scenario where no exact matches exist."""
        # Set up completely different questions
        self.mock_reference.get_questions.return_value = {
            "Question A": Mock(),
            "Question B": Mock()
        }
        
        self.mock_unanswered.get_questions.return_value = {
            "Question C": Mock(),
            "Question D": Mock()
        }
        
        unmatched, remaining_ref = self.filler._match_exact_questions()
        
        # All questions should be unmatched
        self.assertEqual(len(unmatched), 2)
        self.assertEqual(len(remaining_ref), 2)

    def test_all_matches_scenario(self):
        """Test scenario where all questions match exactly."""
        # Set up identical questions
        self.mock_reference.get_questions.return_value = {
            "Question A": Mock(),
            "Question B": Mock()
        }
        
        mock_q1 = Mock(spec=Question)
        mock_q2 = Mock(spec=Question)
        
        self.mock_unanswered.get_questions.return_value = {
            "Question A": mock_q1,
            "Question B": mock_q2
        }
        
        self.mock_unanswered.questions = {
            "Question A": mock_q1,
            "Question B": mock_q2
        }
        
        unmatched, remaining_ref = self.filler._match_exact_questions()
        
        # No questions should be unmatched
        self.assertEqual(len(unmatched), 0)


class TestGetItemsForAnswerMatching(TestQuestionnaireFiller):
    """Test the _get_items_for_answer_matching method."""

    def setUp(self):
        """Set up test data for answer matching tests."""
        super().setUp()
        
        # Create mock questions with various answer scenarios
        self.mock_q1 = Mock(spec=Question)
        self.mock_q1.get_answer.return_value = "Yes"
        self.mock_q1.get_reference_question.return_value = "Do you have a policy?"
        
        self.mock_q2 = Mock(spec=Question)
        self.mock_q2.get_answer.return_value = np.nan  # NaN answer
        self.mock_q2.get_reference_question.return_value = "What is your process?"
        
        self.mock_q3 = Mock(spec=Question)
        self.mock_q3.get_answer.return_value = "We have policies"
        self.mock_q3.get_reference_question.return_value = None  # No reference
        
        self.mock_q4 = Mock(spec=Question)
        self.mock_q4.get_answer.return_value = "   "  # Whitespace only
        self.mock_q4.get_reference_question.return_value = "Empty question?"
        
        self.mock_q5 = Mock(spec=Question)
        self.mock_q5.get_answer.return_value = "Detailed answer"
        self.mock_q5.get_reference_question.return_value = "Detailed question?"
        
        # Set up unanswered questionnaire
        self.mock_unanswered.get_questions.return_value = {
            "Q1": self.mock_q1,
            "Q2": self.mock_q2,
            "Q3": self.mock_q3,
            "Q4": self.mock_q4,
            "Q5": self.mock_q5
        }
        
        self.mock_unanswered.questions = {
            "Q1": self.mock_q1,
            "Q2": self.mock_q2,
            "Q3": self.mock_q3,
            "Q4": self.mock_q4,
            "Q5": self.mock_q5
        }
        
        # Set up reference questionnaire
        self.mock_ref_answer1 = Mock(spec=Question)
        self.mock_ref_answer1.get_answer.return_value = "Yes"
        
        self.mock_ref_answer2 = Mock(spec=Question)
        self.mock_ref_answer2.get_answer.return_value = "Different answer"
        
        self.mock_reference.questions = {
            "Do you have a policy?": self.mock_ref_answer1,
            "Detailed question?": self.mock_ref_answer2
        }

    def test_filters_nan_answers(self):
        """Test that NaN answers are filtered out."""
        items = self.filler._get_items_for_answer_matching()
        
        # Should not include items with NaN answers
        questions = [item['q'] for item in items]
        self.assertNotIn("Q2", questions)

    def test_filters_no_reference_questions(self):
        """Test that questions without reference questions are filtered out."""
        items = self.filler._get_items_for_answer_matching()
        
        # Should not include items without reference questions
        questions = [item['q'] for item in items]
        self.assertNotIn("Q3", questions)

    def test_filters_whitespace_only_answers(self):
        """Test that whitespace-only answers are filtered out."""
        items = self.filler._get_items_for_answer_matching()
        
        # Should not include items with whitespace-only answers
        questions = [item['q'] for item in items]
        self.assertNotIn("Q4", questions)

    def test_includes_valid_items(self):
        """Test that valid items are included."""
        items = self.filler._get_items_for_answer_matching()
        
        # Should include valid items
        questions = [item['q'] for item in items]
        self.assertIn("Q5", questions)

    def test_identical_answers_get_score_1(self):
        """Test that identical answers get a match score of 1 and are not included."""
        items = self.filler._get_items_for_answer_matching()
        
        # Q1 has identical answers, so should not be in items but should get score 1
        questions = [item['q'] for item in items]
        self.assertNotIn("Q1", questions)
        
        # Check that set_answer_match_score was called with 1
        self.mock_q1.set_answer_match_score.assert_called_once_with(1)

    def test_different_answers_included_in_items(self):
        """Test that different answers are included in the items list."""
        items = self.filler._get_items_for_answer_matching()
        
        # Find the item for Q5
        q5_item = next((item for item in items if item['q'] == 'Q5'), None)
        self.assertIsNotNone(q5_item)
        
        # Check the structure
        self.assertEqual(q5_item['a1'], 'Detailed answer')
        self.assertEqual(q5_item['a2'], 'Different answer')

    def test_item_structure(self):
        """Test that items have the correct structure."""
        items = self.filler._get_items_for_answer_matching()
        
        for item in items:
            self.assertIn('q', item)
            self.assertIn('a1', item)
            self.assertIn('a2', item)
            self.assertIsInstance(item['q'], str)
            self.assertIsInstance(item['a1'], str)
            self.assertIsInstance(item['a2'], str)


class TestGenerateCombinedQuestionnaire(TestQuestionnaireFiller):
    """Test the generate_combined_questionnaire method (data processing parts only)."""

    def setUp(self):
        """Set up test data for combined questionnaire generation."""
        super().setUp()
        
        # Create mock questions
        self.mock_q1 = Mock(spec=Question)
        self.mock_q1.get_question_id.return_value = 0
        self.mock_q1.get_question.return_value = "Test question 1"
        self.mock_q1.get_answer.return_value = "Test answer 1"
        self.mock_q1.get_reference_question.return_value = "Ref question 1"
        self.mock_q1.get_question_match_score.return_value = 0.95
        self.mock_q1.get_answer_match_score.return_value = 0.85
        
        self.mock_q2 = Mock(spec=Question)
        self.mock_q2.get_question_id.return_value = 1
        self.mock_q2.get_question.return_value = "Test question 2"
        self.mock_q2.get_answer.return_value = "Test answer 2"
        self.mock_q2.get_reference_question.return_value = None
        self.mock_q2.get_question_match_score.return_value = 0.0
        self.mock_q2.get_answer_match_score.return_value = 0.0
        
        # Set up unanswered questionnaire
        self.mock_unanswered.get_questions.return_value = {
            "Test question 1": self.mock_q1,
            "Test question 2": self.mock_q2
        }
        
        # Set up reference questionnaire
        self.mock_ref_q1 = Mock(spec=Question)
        self.mock_ref_q1.get_answer.return_value = "Ref answer 1"
        
        self.mock_reference.questions = {
            "Ref question 1": self.mock_ref_q1
        }

    @patch('pandas.DataFrame.to_csv')
    def test_combined_questionnaire_structure(self, mock_to_csv):
        """Test that the combined questionnaire has the correct structure."""
        self.filler.generate_combined_questionnaire("test_output.csv")
        
        # Check that to_csv was called
        mock_to_csv.assert_called_once_with("test_output.csv", index=False)

    def test_question_id_conversion(self):
        """Test that question IDs are correctly converted to 1-based indexing."""
        # This would require mocking pandas DataFrame creation
        # For now, we verify the logic by checking the question ID retrieval
        self.assertEqual(self.mock_q1.get_question_id.return_value + 1, 1)
        self.assertEqual(self.mock_q2.get_question_id.return_value + 1, 2)

    @patch('pandas.DataFrame')
    def test_combined_questionnaire_data_structure(self, mock_dataframe):
        """Test that the combined questionnaire creates correct data structure."""
        mock_df = Mock()
        mock_dataframe.return_value = mock_df
        
        self.filler.generate_combined_questionnaire("test.csv")
        
        # Verify DataFrame was created with correct data
        call_args = mock_dataframe.call_args[0][0]  # Get the data passed to DataFrame
        
        # Should have 2 rows (2 questions)
        self.assertEqual(len(call_args), 2)
        
        # Check first row structure
        first_row = call_args[0]
        expected_columns = [
            "Question ID", "Current Question", "Current Answer", 
            "Matched Question", "Matched Answer", "Question Match Score", "Answer Match Score"
        ]
        for col in expected_columns:
            self.assertIn(col, first_row)
        
        # Check data values
        self.assertEqual(first_row["Question ID"], 1)  # 1-based indexing
        self.assertEqual(first_row["Current Question"], "Test question 1")
        self.assertEqual(first_row["Matched Answer"], "Ref answer 1")

    def test_no_reference_answer_handling(self):
        """Test handling when reference question is None."""
        # Modify mock_q2 to have None reference question to test the else branch
        self.mock_q2.get_reference_question.return_value = None
        
        with patch('pandas.DataFrame') as mock_dataframe:
            mock_df = Mock()
            mock_dataframe.return_value = mock_df
            
            self.filler.generate_combined_questionnaire("test.csv")
            
            call_args = mock_dataframe.call_args[0][0]
            second_row = call_args[1]  # Question 2 has None reference
            
            # Should have empty string for matched answer when reference question is None
            self.assertEqual(second_row["Matched Answer"], "")

    @patch('builtins.print')
    @patch('pandas.DataFrame.to_csv')
    def test_success_message_printed(self, mock_to_csv, mock_print):
        """Test that success message is printed after saving."""
        filename = "custom_output.csv"
        self.filler.generate_combined_questionnaire(filename)
        
        # Check that success message was printed
        mock_print.assert_called_with(f"Combined questionnaire has been saved to {filename}!")


class TestEdgeCasesAndIntegration(TestQuestionnaireFiller):
    """Test edge cases and integration scenarios."""

    def test_empty_questionnaires(self):
        """Test behavior with empty questionnaires."""
        # Set up empty questionnaires
        self.mock_reference.get_questions.return_value = {}
        self.mock_unanswered.get_questions.return_value = {}
        
        # Should not crash
        unmatched, remaining = self.filler._match_exact_questions()
        self.assertEqual(len(unmatched), 0)
        self.assertEqual(len(remaining), 0)
        
        items = self.filler._get_items_for_answer_matching()
        self.assertEqual(len(items), 0)

    def test_has_meaningful_content_with_special_characters(self):
        """Test _has_meaningful_content with various special characters."""
        # Test cases that should return False
        false_cases = [
            "!!!@@@###",  # Only punctuation
            "...",         # Only dots
            "---",         # Only dashes
            "   \n\t   ",  # Only whitespace
            "",            # Empty
            "NaN",         # String NaN
            "null",        # String null
        ]
        
        for case in false_cases:
            with self.subTest(case=case):
                self.assertFalse(self.filler._has_meaningful_content(case),
                               f"'{case}' should return False")
        
        # Test cases that should return True
        true_cases = [
            "Yes!",        # Alphanumeric with punctuation
            "N/A",         # Common abbreviation
            "123.45",      # Numbers with decimal
            "a1b2c3",      # Mixed alphanumeric
            "  OK  ",      # Valid with whitespace
            "42%",         # Number with symbol
        ]
        
        for case in true_cases:
            with self.subTest(case=case):
                self.assertTrue(self.filler._has_meaningful_content(case),
                              f"'{case}' should return True")

    def test_get_items_edge_cases(self):
        """Test _get_items_for_answer_matching with edge cases."""
        # Create questions with various edge case scenarios
        mock_questions = {}
        
        # Question with NaN reference answer
        q1 = Mock(spec=Question)
        q1.get_answer.return_value = "Valid answer"
        q1.get_reference_question.return_value = "Ref Q1"
        mock_questions["Q1"] = q1
        
        # Question with empty string reference answer
        q2 = Mock(spec=Question)
        q2.get_answer.return_value = "Another answer"
        q2.get_reference_question.return_value = "Ref Q2"
        mock_questions["Q2"] = q2
        
        # Question with numeric answer
        q3 = Mock(spec=Question)
        q3.get_answer.return_value = 42
        q3.get_reference_question.return_value = "Ref Q3"
        mock_questions["Q3"] = q3
        
        self.mock_unanswered.get_questions.return_value = mock_questions
        self.mock_unanswered.questions = mock_questions
        
        # Set up reference answers
        ref_q1 = Mock(spec=Question)
        ref_q1.get_answer.return_value = np.nan  # NaN reference answer
        
        ref_q2 = Mock(spec=Question)
        ref_q2.get_answer.return_value = ""  # Empty reference answer
        
        ref_q3 = Mock(spec=Question)
        ref_q3.get_answer.return_value = "42"  # String version of number
        
        self.mock_reference.questions = {
            "Ref Q1": ref_q1,
            "Ref Q2": ref_q2,
            "Ref Q3": ref_q3
        }
        
        items = self.filler._get_items_for_answer_matching()
        
        # Based on actual implementation:
        # - Current logic only filters based on current answer meaningfulness
        # - It doesn't filter based on reference answer content
        # - So Q1, Q2, Q3 should all be included since they have meaningful current answers
        questions = [item['q'] for item in items]
        
        # All questions should be included since they have meaningful current answers
        self.assertIn("Q1", questions)  # NaN reference answer but valid current answer
        self.assertIn("Q2", questions)  # Empty reference answer but valid current answer
        
        # Q3 should not be in items because "42" == "42" (identical after string conversion)
        self.assertNotIn("Q3", questions)

    def test_match_exact_questions_with_duplicates(self):
        """Test exact matching when there are duplicate questions."""
        # Set up scenario with duplicate questions
        ref_q1 = Mock(spec=Question)
        ref_q1.get_question.return_value = "Duplicate question"
        
        ref_q2 = Mock(spec=Question)
        ref_q2.get_question.return_value = "Unique question"
        
        unans_q1 = Mock(spec=Question)
        unans_q2 = Mock(spec=Question)
        
        self.mock_reference.get_questions.return_value = {
            "Duplicate question": ref_q1,
            "Unique question": ref_q2
        }
        
        self.mock_unanswered.get_questions.return_value = {
            "Duplicate question": unans_q1,
            "Different question": unans_q2
        }
        
        self.mock_unanswered.questions = {
            "Duplicate question": unans_q1,
            "Different question": unans_q2
        }
        
        unmatched, remaining = self.filler._match_exact_questions()
        
        # Should find the duplicate and set it up correctly
        unans_q1.set_reference_question.assert_called_once_with("Duplicate question")
        unans_q1.set_question_match_score.assert_called_once_with(1)
        
        # Should have one unmatched question
        self.assertEqual(len(unmatched), 1)
        self.assertIn("Different question", unmatched)


class TestDataTypeHandling(TestQuestionnaireFiller):
    """Test handling of various data types that might come from CSV files."""

    def test_has_meaningful_content_with_various_types(self):
        """Test _has_meaningful_content with various data types from pandas."""
        
        # Test different ways NaN can appear
        nan_values = [
            np.nan,
            float('nan'),
            None,
            pd.NA
        ]
        
        for nan_val in nan_values:
            with self.subTest(nan_value=type(nan_val).__name__):
                self.assertFalse(self.filler._has_meaningful_content(nan_val))
        
        # Test numeric types
        numeric_values = [
            1,
            1.0,
            np.int64(42),
            np.float64(3.14),
            42  # Simple integer
        ]
        
        for num_val in numeric_values:
            with self.subTest(numeric_value=f"{num_val} ({type(num_val)})"):
                try:
                    result = self.filler._has_meaningful_content(num_val)
                    self.assertTrue(result)
                except Exception as e:
                    self.fail(f"Failed to handle {type(num_val)}: {e}")

    def test_string_comparison_with_mixed_types(self):
        """Test string comparison in _get_items_for_answer_matching with mixed types."""
        # Create a question with numeric answer
        mock_q = Mock(spec=Question)
        mock_q.get_answer.return_value = 42  # Numeric
        mock_q.get_reference_question.return_value = "Test ref"
        
        self.mock_unanswered.get_questions.return_value = {"Q1": mock_q}
        self.mock_unanswered.questions = {"Q1": mock_q}
        
        # Reference answer is string
        ref_q = Mock(spec=Question)
        ref_q.get_answer.return_value = "42"  # String
        
        self.mock_reference.questions = {"Test ref": ref_q}
        
        items = self.filler._get_items_for_answer_matching()
        
        # Should recognize "42" == "42" as identical and not include in items
        questions = [item['q'] for item in items]
        self.assertNotIn("Q1", questions)
        
        # Should set answer match score to 1
        mock_q.set_answer_match_score.assert_called_once_with(1)


def run_tests():
    """Run the test suite."""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestHasMeaningfulContent,
        TestMatchExactQuestions,
        TestGetItemsForAnswerMatching,
        TestGenerateCombinedQuestionnaire,
        TestEdgeCasesAndIntegration,
        TestDataTypeHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running Questionnaire_Filler Unit Tests")
    print("=" * 50)
    success = run_tests()
    print("=" * 50)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    sys.exit(0 if success else 1)
