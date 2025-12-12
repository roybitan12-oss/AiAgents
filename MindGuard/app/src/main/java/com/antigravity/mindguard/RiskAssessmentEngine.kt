package com.antigravity.mindguard

class RiskAssessmentEngine {

    companion object {
        const val RISK_LOW = 0.3
        const val RISK_MODERATE = 0.6
        const val RISK_HIGH = 0.85
    }

    data class RiskResult(
        val score: Double,
        val level: String,
        val recommendation: String,
        val isCrisis: Boolean
    )

    fun calculateRisk(
        voiceStress: Double, // 0.0 to 1.0 (Mocked input)
        sleepQuality: Int,   // 0 to 10 (10 is best)
        sentimentScore: Double // 0.0 (Negative) to 1.0 (Positive)
    ): RiskResult {
        
        // Normalize Sleep: 10 is good (0 risk), 0 is bad (1 risk)
        val sleepRisk = (10 - sleepQuality) / 10.0
        
        // Sentiment: 1.0 is good (0 risk), 0.0 is bad (1 risk)
        val textRisk = 1.0 - sentimentScore

        // Weighted Average
        // Voice: 30%, Sleep: 30%, Text: 40%
        val totalRisk = (voiceStress * 0.3) + (sleepRisk * 0.3) + (textRisk * 0.4)

        return when {
            totalRisk >= RISK_HIGH -> RiskResult(
                totalRisk, 
                "HIGH", 
                "Immediate support recommended.", 
                true
            )
            totalRisk >= RISK_MODERATE -> RiskResult(
                totalRisk, 
                "MODERATE", 
                "Consider a breathing exercise.", 
                false
            )
            else -> RiskResult(
                totalRisk, 
                "LOW", 
                "You are doing well!", 
                false
            )
        }
    }
}
