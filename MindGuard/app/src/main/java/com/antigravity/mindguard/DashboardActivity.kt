package com.antigravity.mindguard

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class DashboardActivity : AppCompatActivity() {

    private val riskEngine = RiskAssessmentEngine()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        // Initial Dummy Data (Safe State)
        updateRiskUI(riskEngine.calculateRisk(0.1, 8, 0.9))

        findViewById<Button>(R.id.btnSimulateCrisis).setOnClickListener {
            // Simulate High Risk: High Voice Stress (0.9), Bad Sleep (2), Negative Text (0.1)
            val result = riskEngine.calculateRisk(0.9, 2, 0.1)
            updateRiskUI(result)
            
            if (result.isCrisis) {
                startActivity(Intent(this, CrisisActivity::class.java))
            }
        }
        
        findViewById<Button>(R.id.btnCheckIn).setOnClickListener {
             // Mock Check-in processing
        }
    }

    private fun updateRiskUI(result: RiskAssessmentEngine.RiskResult) {
        val txtRisk = findViewById<TextView>(R.id.txtRiskLevel)
        txtRisk.text = result.level
        
        when (result.level) {
            "LOW" -> txtRisk.setTextColor(Color.parseColor("#388E3C")) // Green
            "MODERATE" -> txtRisk.setTextColor(Color.parseColor("#FFA000")) // Amber
            "HIGH" -> txtRisk.setTextColor(Color.parseColor("#D32F2F")) // Red
        }
    }
}
