"""
Tests for explainability services
"""
from app.services.explain import ExplainService
from app.models.registry import ModelRegistry


def test_local_shap_structure():
    """Test that local SHAP returns expected structure"""
    registry = ModelRegistry()
    service = ExplainService(registry)
    
    contributions = service.compute_local_shap(37.5, -122.0, "2024-01-15")
    
    # Check that we get a list of contributions
    assert isinstance(contributions, list)
    assert len(contributions) > 0
    
    # Check structure of first contribution
    contrib = contributions[0]
    assert hasattr(contrib, 'feature')
    assert hasattr(contrib, 'value')
    assert hasattr(contrib, 'unit')
    assert hasattr(contrib, 'contribution')


def test_interactions():
    """Test that interactions are computed"""
    registry = ModelRegistry()
    service = ExplainService(registry)
    
    interactions = service.compute_interactions(37.5, -122.0, "2024-01-15")
    
    assert isinstance(interactions, list)
    assert len(interactions) > 0
    
    # Check structure
    interaction = interactions[0]
    assert hasattr(interaction, 'pair')
    assert hasattr(interaction, 'value')
    assert len(interaction.pair) == 2


def test_ood_check():
    """Test OOD detection"""
    registry = ModelRegistry()
    service = ExplainService(registry)
    
    ood = service.check_ood(37.5, -122.0, "2024-01-15")
    
    # Should return boolean
    assert isinstance(ood, bool)
