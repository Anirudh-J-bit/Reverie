class GreenScoreCalculator:
    """
    Calculates a Green Score (0 - 100) evaluating efficiency per request.
    """

    @staticmethod
    def calculate_score(complexity: str, pct_energy_saved: float) -> int:
        base_scores = {
            "LOW": 95,     # Maximum efficiency achieved
            "MEDIUM": 85,  # Balanced efficiency
            "HIGH": 70     # High compute needed, lower eco-savings relative to baseline
        }
        
        score = base_scores.get(complexity, 80)
        
        # Adjust slightly based on percent saved
        score += int(pct_energy_saved * 0.05)
        
        # Clamp score between 0 and 100
        return max(0, min(100, score))
    