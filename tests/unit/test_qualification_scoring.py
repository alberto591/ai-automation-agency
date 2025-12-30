from application.services.scoring import ScoringService
from domain.qualification import (
    FinancingStatus,
    Intent,
    LeadCategory,
    QualificationData,
    Timeline,
)


def test_hot_lead_scenario():
    """Test a perfect HOT lead scenario (Max score potential)."""
    data = QualificationData(
        intent=Intent.BUY,  # +3
        timeline=Timeline.URGENT,  # +3
        budget=400_000,  # +3 (>300k)
        financing=FinancingStatus.APPROVED,  # +3
        location_specific=True,  # +2
        property_specific=True,  # +2
        has_contact_info=True,  # +2
    )
    # Total Raw: 18 -> Normalized: 10

    result = ScoringService.calculate_score(data)

    assert result.raw_score == 18
    assert result.normalized_score == 10
    assert result.category == LeadCategory.HOT
    assert "Call within 5 minutes" in result.action_item


def test_warm_lead_scenario():
    """Test an average WARM lead scenario."""
    data = QualificationData(
        intent=Intent.BUY,  # +3
        timeline=Timeline.MEDIUM,  # +2
        budget=150_000,  # +2 (100k-300k)
        financing=FinancingStatus.TODO,  # +1
        location_specific=False,  # 0
        property_specific=False,  # 0
        has_contact_info=True,  # +2 (implied)
    )
    # Total Raw: 3+2+2+1+0+0+2 (assuming contact) = 10
    # Normalized: (10/18)*10 = 5.55 -> rounds to 6?
    # Logic in service: min(10, math.ceil((score / 18) * 10))
    # 10/18 = 0.555 -> *10 = 5.55 -> ceil = 6.

    result = ScoringService.calculate_score(data)

    assert result.raw_score == 10
    assert result.normalized_score == 6
    assert result.category == LeadCategory.WARM


def test_cold_lead_scenario():
    """Test a COLD lead (Rental, Long timeline, Low budget)."""
    data = QualificationData(
        intent=Intent.RENT,  # +1
        timeline=Timeline.LONG,  # +1
        budget=None,  # +0
        financing=FinancingStatus.UNKNOWN,  # 0
        location_specific=False,  # 0
        property_specific=False,  # 0
        has_contact_info=True,  # +2 (we have their phone)
    )
    # Total Raw: 1+1+0+0+0+0+2 = 4
    # Normalized: (4/18)*10 = 2.2 -> ceil = 3

    result = ScoringService.calculate_score(data)

    assert result.raw_score == 4
    assert result.normalized_score <= 3
    assert result.category == LeadCategory.COLD


def test_disqualified_lead():
    """Test disqualification logic (Low budget + Buy)."""
    data = QualificationData(
        intent=Intent.BUY,
        budget=30_000,  # < 50k threshold
        timeline=Timeline.UNKNOWN,
        financing=FinancingStatus.UNKNOWN,
    )

    result = ScoringService.calculate_score(data)

    assert result.category == LeadCategory.DISQUALIFIED
    assert "Disqualified" in result.action_item
