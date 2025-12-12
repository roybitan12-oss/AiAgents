package com.antigravity.mindguard

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity

class OnboardingActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_onboarding)

        findViewById<Button>(R.id.btnContinue).setOnClickListener {
            // In a real app, save consent preferences here
            startActivity(Intent(this, DashboardActivity::class.java))
            finish()
        }
    }
}
