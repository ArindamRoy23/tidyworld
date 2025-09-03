"""Test module for extractor.py agents and functions.

This module tests the entity and relationship extraction functionality including:
- Individual agent configurations and initialization
- The check_extraction_complete function
- Agent interactions and state management
- Edge cases and error handling
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools import ToolContext


class TestCheckExtractionComplete(unittest.TestCase):
    """Test cases for the check_extraction_complete function."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Import the function to test
        from tidyworld._agents.extractor import check_extraction_complete

        self.check_extraction_complete = check_extraction_complete

        # Create mock ToolContext
        self.mock_tool_context = Mock(spec=ToolContext)
        self.mock_tool_context.state = {}
        self.mock_tool_context.actions = Mock()
        self.mock_tool_context.actions.escalate = False

    def test_extraction_complete_with_no_missed_items(self):
        """Test that extraction completes when no missed entities or relationships exist."""
        # Arrange
        self.mock_tool_context.state = {"missed_entities": [], "missed_relationships": []}

        # Act
        result = self.check_extraction_complete(self.mock_tool_context)

        # Assert
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["message"], "Extraction finished")
        self.assertTrue(self.mock_tool_context.actions.escalate)

    def test_extraction_continues_with_missed_entities(self):
        """Test that extraction continues when missed entities exist."""
        # Arrange
        self.mock_tool_context.state = {"missed_entities": ["entity1", "entity2"], "missed_relationships": []}

        # Act
        result = self.check_extraction_complete(self.mock_tool_context)

        # Assert
        self.assertEqual(result["status"], "continue")
        self.assertEqual(result["missed_entities"], 2)
        self.assertEqual(result["missed_relationships"], 0)
        self.assertFalse(self.mock_tool_context.actions.escalate)

    def test_extraction_continues_with_missed_relationships(self):
        """Test that extraction continues when missed relationships exist."""
        # Arrange
        self.mock_tool_context.state = {"missed_entities": [], "missed_relationships": ["rel1", "rel2", "rel3"]}

        # Act
        result = self.check_extraction_complete(self.mock_tool_context)

        # Assert
        self.assertEqual(result["status"], "continue")
        self.assertEqual(result["missed_entities"], 0)
        self.assertEqual(result["missed_relationships"], 3)
        self.assertFalse(self.mock_tool_context.actions.escalate)

    def test_extraction_continues_with_both_missed_items(self):
        """Test that extraction continues when both missed entities and relationships exist."""
        # Arrange
        self.mock_tool_context.state = {"missed_entities": ["entity1"], "missed_relationships": ["rel1", "rel2"]}

        # Act
        result = self.check_extraction_complete(self.mock_tool_context)

        # Assert
        self.assertEqual(result["status"], "continue")
        self.assertEqual(result["missed_entities"], 1)
        self.assertEqual(result["missed_relationships"], 2)
        self.assertFalse(self.mock_tool_context.actions.escalate)

    def test_extraction_with_missing_state_keys(self):
        """Test behavior when state keys are missing (default to empty lists)."""
        # Arrange
        self.mock_tool_context.state = {}

        # Act
        result = self.check_extraction_complete(self.mock_tool_context)

        # Assert
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["message"], "Extraction finished")
        self.assertTrue(self.mock_tool_context.actions.escalate)

    def test_extraction_with_none_values(self):
        """Test behavior when state values are None."""
        # Arrange
        self.mock_tool_context.state = {"missed_entities": None, "missed_relationships": None}

        # Act
        result = self.check_extraction_complete(self.mock_tool_context)

        # Assert
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["message"], "Extraction finished")
        self.assertTrue(self.mock_tool_context.actions.escalate)


class TestExtractorAgents(unittest.TestCase):
    """Test cases for the extractor agents configuration and behavior."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the LLM service to avoid actual API calls
        self.mock_llm_service_patcher = patch("tidyworld._agents.extractor.DefaultLLMService")
        self.mock_llm_service = self.mock_llm_service_patcher.start()

        # Mock the LLM model
        self.mock_llm = Mock()
        self.mock_llm_service.return_value.get_model.return_value = self.mock_llm

        # Import after patching to ensure mocks are in place
        from tidyworld._agents import extractor

        self.extractor_module = extractor

    def tearDown(self):
        """Clean up after each test method."""
        self.mock_llm_service_patcher.stop()

    def test_initial_extractor_configuration(self):
        """Test that the initial extractor agent is properly configured."""
        initial_extractor = self.extractor_module.initial_extractor

        self.assertIsInstance(initial_extractor, LlmAgent)
        self.assertEqual(initial_extractor.name, "InitialExtractor")
        self.assertEqual(initial_extractor.model, self.mock_llm)
        self.assertIn("extract all entities and relationships", initial_extractor.instruction.lower())
        self.assertEqual(initial_extractor.output_key, "current_graph")

    def test_review_agent_configuration(self):
        """Test that the review agent is properly configured."""
        review_agent = self.extractor_module.review_agent

        self.assertIsInstance(review_agent, LlmAgent)
        self.assertEqual(review_agent.name, "ReviewAgent")
        self.assertEqual(review_agent.model, self.mock_llm)
        self.assertIn("thorough reviewer", review_agent.instruction.lower())
        self.assertEqual(review_agent.output_key, "missed_entities")

    def test_refinement_agent_configuration(self):
        """Test that the refinement agent is properly configured."""
        refinement_agent = self.extractor_module.refinement_agent

        self.assertIsInstance(refinement_agent, LlmAgent)
        self.assertEqual(refinement_agent.name, "RefinementAgent")
        self.assertEqual(refinement_agent.model, self.mock_llm)
        self.assertIn("refining information extraction", refinement_agent.instruction.lower())
        self.assertEqual(refinement_agent.output_key, "current_graph")

    def test_extraction_loop_configuration(self):
        """Test that the extraction loop is properly configured."""
        extraction_loop = self.extractor_module.extraction_loop

        self.assertIsInstance(extraction_loop, LoopAgent)
        self.assertEqual(extraction_loop.name, "EntityExtractionLoop")
        self.assertEqual(len(extraction_loop.sub_agents), 2)
        self.assertEqual(extraction_loop.max_iterations, 5)

    def test_root_agent_configuration(self):
        """Test that the root agent is properly configured."""
        root_agent = self.extractor_module.root_agent

        self.assertIsInstance(root_agent, LlmAgent)
        self.assertEqual(root_agent.name, "EntityExtractor")
        self.assertEqual(root_agent.model, self.mock_llm)
        self.assertEqual(len(root_agent.tools), 1)
        self.assertEqual(root_agent.tools[0].__name__, "check_extraction_complete")

    def test_state_constants(self):
        """Test that state constants are properly defined."""
        self.assertEqual(self.extractor_module.STATE_CURRENT_GRAPH, "current_graph")
        self.assertEqual(self.extractor_module.STATE_DOCUMENT, "document")
        self.assertEqual(self.extractor_module.STATE_ENTITY_TYPES, "entity_types")
        self.assertEqual(self.extractor_module.STATE_MISSED_ENTITIES, "missed_entities")
        self.assertEqual(self.extractor_module.STATE_MISSED_RELATIONSHIPS, "missed_relationships")

    def test_exported_agents(self):
        """Test that all required agents are exported."""
        expected_exports = ["root_agent", "extraction_loop", "initial_extractor", "review_agent", "refinement_agent"]

        for export in expected_exports:
            self.assertTrue(hasattr(self.extractor_module, export))
            self.assertIn(export, self.extractor_module.__all__)


class TestExtractorIntegration(unittest.TestCase):
    """Integration tests for the extractor module with realistic scenarios."""

    def setUp(self):
        """Set up test fixtures for integration tests."""
        # Mock the LLM service
        self.mock_llm_service_patcher = patch("tidyworld._agents.extractor.DefaultLLMService")
        self.mock_llm_service = self.mock_llm_service_patcher.start()

        # Mock the LLM model with realistic responses
        self.mock_llm = Mock()
        self.mock_llm_service.return_value.get_model.return_value = self.mock_llm

        from tidyworld._agents.extractor import check_extraction_complete

        self.check_extraction_complete = check_extraction_complete

    def tearDown(self):
        """Clean up after integration tests."""
        self.mock_llm_service_patcher.stop()

    def test_realistic_extraction_scenario(self):
        """Test a realistic extraction scenario with sample data."""
        # Sample data that might be used in actual extraction
        sample_document = "John works at Microsoft as a software engineer. He collaborates with Sarah on AI projects."
        sample_entity_types = ["PERSON", "ORGANIZATION", "ROLE", "PROJECT"]

        # Mock ToolContext with realistic state
        mock_context = Mock(spec=ToolContext)
        mock_context.state = {
            "document": sample_document,
            "entity_types": sample_entity_types,
            "current_graph": {
                "entities": [
                    {"name": "JOHN", "type": "PERSON", "desc": "Software engineer at Microsoft"},
                    {"name": "MICROSOFT", "type": "ORGANIZATION", "desc": "Technology company"},
                ],
                "relationships": [{"source": "JOHN", "target": "MICROSOFT", "desc": "works at"}],
            },
            "missed_entities": ["SARAH"],
            "missed_relationships": ["collaboration relationship"],
        }
        mock_context.actions = Mock()
        mock_context.actions.escalate = False

        # Test that extraction continues when there are missed items
        result = self.check_extraction_complete(mock_context)

        self.assertEqual(result["status"], "continue")
        self.assertEqual(result["missed_entities"], 1)
        self.assertEqual(result["missed_relationships"], 1)
        self.assertFalse(mock_context.actions.escalate)

    def test_extraction_completion_scenario(self):
        """Test extraction completion with fully extracted graph."""
        # Complete extraction state
        mock_context = Mock(spec=ToolContext)
        mock_context.state = {
            "document": "John works at Microsoft.",
            "entity_types": ["PERSON", "ORGANIZATION"],
            "current_graph": {
                "entities": [
                    {"name": "JOHN", "type": "PERSON", "desc": "Software engineer"},
                    {"name": "MICROSOFT", "type": "ORGANIZATION", "desc": "Technology company"},
                ],
                "relationships": [{"source": "JOHN", "target": "MICROSOFT", "desc": "works at"}],
            },
            "missed_entities": [],  # No missed entities
            "missed_relationships": [],  # No missed relationships
        }
        mock_context.actions = Mock()
        mock_context.actions.escalate = False

        # Test that extraction completes
        result = self.check_extraction_complete(mock_context)

        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["message"], "Extraction finished")
        self.assertTrue(mock_context.actions.escalate)

    def test_agent_instruction_templates(self):
        """Test that agent instructions contain the expected template variables."""
        from tidyworld._agents import extractor

        # Check initial extractor instruction contains expected variables
        initial_instruction = extractor.initial_extractor.instruction
        self.assertIn("{document}", initial_instruction)
        self.assertIn("{entity_types}", initial_instruction)

        # Check review agent instruction contains expected variables
        review_instruction = extractor.review_agent.instruction
        self.assertIn("{current_graph}", review_instruction)
        self.assertIn("{document}", review_instruction)
        self.assertIn("{entity_types}", review_instruction)

        # Check refinement agent instruction contains expected variables
        refinement_instruction = extractor.refinement_agent.instruction
        self.assertIn("{current_graph}", refinement_instruction)
        self.assertIn("{document}", refinement_instruction)
        self.assertIn("{entity_types}", refinement_instruction)
        self.assertIn("{missed_entities}", refinement_instruction)
        self.assertIn("{missed_relationships}", refinement_instruction)


class TestExtractorEdgeCases(unittest.TestCase):
    """Test edge cases and error scenarios for the extractor module."""

    def setUp(self):
        """Set up test fixtures for edge case tests."""
        from tidyworld._agents.extractor import check_extraction_complete

        self.check_extraction_complete = check_extraction_complete

    def test_malformed_state_data(self):
        """Test behavior with malformed state data."""
        mock_context = Mock(spec=ToolContext)
        mock_context.actions = Mock()
        mock_context.actions.escalate = False

        # Test with non-list values
        mock_context.state = {"missed_entities": "not_a_list", "missed_relationships": 123}

        # Should handle gracefully and treat as truthy (non-empty)
        result = self.check_extraction_complete(mock_context)

        self.assertEqual(result["status"], "continue")
        self.assertFalse(mock_context.actions.escalate)

    def test_empty_state(self):
        """Test behavior with completely empty state."""
        mock_context = Mock(spec=ToolContext)
        mock_context.state = {}
        mock_context.actions = Mock()
        mock_context.actions.escalate = False

        result = self.check_extraction_complete(mock_context)

        self.assertEqual(result["status"], "complete")
        self.assertTrue(mock_context.actions.escalate)

    def test_large_missed_items_list(self):
        """Test behavior with large lists of missed items."""
        mock_context = Mock(spec=ToolContext)
        mock_context.actions = Mock()
        mock_context.actions.escalate = False

        # Create large lists
        large_entities = [f"entity_{i}" for i in range(1000)]
        large_relationships = [f"rel_{i}" for i in range(500)]

        mock_context.state = {"missed_entities": large_entities, "missed_relationships": large_relationships}

        result = self.check_extraction_complete(mock_context)

        self.assertEqual(result["status"], "continue")
        self.assertEqual(result["missed_entities"], 1000)
        self.assertEqual(result["missed_relationships"], 500)
        self.assertFalse(mock_context.actions.escalate)

    def test_tool_context_missing_actions(self):
        """Test behavior when ToolContext is missing actions attribute."""
        mock_context = Mock(spec=ToolContext)
        mock_context.state = {"missed_entities": [], "missed_relationships": []}
        # Deliberately not setting actions attribute
        delattr(mock_context, "actions")

        # Should still complete but might raise AttributeError
        with self.assertRaises(AttributeError):
            self.check_extraction_complete(mock_context)

    def test_import_structure(self):
        """Test that the module can be imported correctly."""
        try:
            from tidyworld._agents.extractor import (
                check_extraction_complete,
                extraction_loop,
                initial_extractor,
                refinement_agent,
                review_agent,
                root_agent,
            )
        except ImportError as e:
            self.fail(f"Failed to import extractor components: {e}")

    def test_llm_service_configuration(self):
        """Test that LLM service is configured with correct model."""
        with patch("tidyworld._agents.extractor.DefaultLLMService") as mock_service:
            mock_service.return_value.get_model.return_value = Mock()

            # Re-import to trigger the LLM service initialization
            import importlib

            import tidyworld._agents.extractor

            importlib.reload(tidyworld._agents.extractor)

            # Verify that the service was called with correct model
            mock_service.assert_called_with(model="groq/qwen/qwen3-32b")


class TestExtractorTypes(unittest.TestCase):
    """Test type compatibility and structure validation."""

    def test_function_signature(self):
        """Test that check_extraction_complete has the correct signature."""
        import inspect

        from tidyworld._agents.extractor import check_extraction_complete

        signature = inspect.signature(check_extraction_complete)
        parameters = list(signature.parameters.keys())

        self.assertEqual(len(parameters), 1)
        self.assertEqual(parameters[0], "tool_context")

        # Check parameter type annotation
        param = signature.parameters["tool_context"]
        self.assertEqual(param.annotation, ToolContext)

    def test_return_type_structure(self):
        """Test that the function returns the expected dictionary structure."""
        from tidyworld._agents.extractor import check_extraction_complete

        mock_context = Mock(spec=ToolContext)
        mock_context.state = {"missed_entities": [], "missed_relationships": []}
        mock_context.actions = Mock()
        mock_context.actions.escalate = False

        result = check_extraction_complete(mock_context)

        # Test return type is dictionary
        self.assertIsInstance(result, dict)

        # Test required keys are present
        self.assertIn("status", result)

        # Test status values are valid
        self.assertIn(result["status"], ["complete", "continue"])


if __name__ == "__main__":
    # Configure test discovery and execution
    unittest.main(verbosity=2, buffer=True)
