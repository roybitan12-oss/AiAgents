package com.antigravity.mindguard

import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class CrisisActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_crisis)

        findViewById<Button>(R.id.btnSOS).setOnClickListener {
            Toast.makeText(this, "Calling Emergency Services...", Toast.LENGTH_LONG).show()
        }

        findViewById<Button>(R.id.btnTherapist).setOnClickListener {
            Toast.makeText(this, "Dialing Provider...", Toast.LENGTH_SHORT).show()
        }
    }
}
