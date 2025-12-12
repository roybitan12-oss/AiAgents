package com.antigravity.mindguard

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Simple routing logic: Always go to Onboarding for prototype
        startActivity(Intent(this, OnboardingActivity::class.java))
        finish()
    }
}
