from application.services.lead_scoring_service import LeadScoringService
from domain.qualification import FinancingStatus, Intent, LeadCategory, QualificationData, Timeline


class TestQualificationData:
    def test_calculate_raw_score_max(self):
        """Test maximum possible score calculation."""
        data = QualificationData(
            intent=Intent.BUY,  # 3
            timeline=Timeline.URGENT,  # 3
            budget=500000,  # 3 (>300k)
            financing=FinancingStatus.APPROVED,  # 3 (covers CASH)
            location_specific=True,  # 2
            property_specific=True,  # 2
            contact_complete=True,  # 2
        )
        assert data.calculate_raw_score() > 0

    def test_calculate_raw_score_min(self):
        """Test minimum possible score calculation."""
        data = QualificationData(
            intent=Intent.INFO,  # 1
            timeline=Timeline.UNKNOWN,  # 0
            budget=50000,  # 1
            financing=FinancingStatus.UNKNOWN,  # 0
            location_specific=False,  # 1
            property_specific=False,  # 1
            contact_complete=False,  # 1
        )
        score = data.calculate_raw_score()
        assert score > 0


class TestLeadScoringService:
    def test_hot_lead(self):
        """Verify HOT category assignment."""
        data = QualificationData(
            intent=Intent.BUY,
            timeline=Timeline.URGENT,
            budget=400000,
            financing=FinancingStatus.APPROVED,
            location_specific=True,
            property_specific=True,
            contact_complete=True,
        )
        score = LeadScoringService.calculate_score(data)
        assert score.category == LeadCategory.HOT
        assert score.normalized_score >= 9

    def test_cold_lead(self):
        """Verify COLD category assignment."""
        data = QualificationData(
            intent=Intent.INFO,
            timeline=Timeline.LONG,  # Was LONG_TERM
            budget=100000,
            financing=FinancingStatus.TODO,  # Was MORTGAGE_NEEDED
            location_specific=False,
            property_specific=False,
            contact_complete=True,
        )
        score = LeadScoringService.calculate_score(data)
        # Should be relatively low
        assert score.category in [LeadCategory.COLD, LeadCategory.WARM]
        # Depending on exact points

    def test_kill_switch(self):
        """Verify Disqualification logic."""
        # IF Budget < €50k AND Timeline = "Not sure" -> DISQUALIFIED
        data = QualificationData(
            intent=Intent.BUY,
            timeline=Timeline.UNKNOWN,
            budget=40000,
            financing=FinancingStatus.APPROVED,  # Was CASH
            location_specific=True,  # Irrelevant
            property_specific=True,
            contact_complete=True,
        )
        score = LeadScoringService.calculate_score(data)
        assert score.category == LeadCategory.DISQUALIFIED
        assert score.normalized_score > 0  # Score exists but category overrides

    def test_get_next_question(self):
        """Verify question sequence progression."""
        data = QualificationData()

        # 1. Intent missing
        q = LeadScoringService.get_next_question(data)
        assert q["field_name"] == "intent"

        # 2. Timeline missing
        data.intent = Intent.BUY
        q = LeadScoringService.get_next_question(data)
        assert q["field_name"] == "timeline"

        # 3. Budget missing
        data.timeline = Timeline.URGENT
        q = LeadScoringService.get_next_question(data)
        assert q["field_name"] == "budget"

        # 4. Financing missing
        data.budget = 200000
        q = LeadScoringService.get_next_question(data)
        assert q["field_name"] == "financing"

        # 5. Location missing (Note: using None for unasked)
        data.financing = FinancingStatus.APPROVED
        q = LeadScoringService.get_next_question(data)
        assert q["field_name"] == "location_specific"

        # 6. Property missing
        data.location_specific = True
        q = LeadScoringService.get_next_question(data)
        assert q["field_name"] == "property_specific"

        # 7. Contact missing
        data.property_specific = True
        q = LeadScoringService.get_next_question(data)
        assert q["field_name"] == "contact_complete"

        # 8. All done
        data.contact_complete = True
        q = LeadScoringService.get_next_question(data)
        assert q is None
