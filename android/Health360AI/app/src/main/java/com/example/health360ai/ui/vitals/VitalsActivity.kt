package com.example.health360ai.ui.vitals

import android.content.Intent
import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.health360ai.data.repository.CheckupStateRepository
import com.example.health360ai.databinding.ActivityVitalsBinding
import com.example.health360ai.ui.image.ImageInputActivity

class VitalsActivity : AppCompatActivity() {

    private lateinit var binding: ActivityVitalsBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityVitalsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupDropdowns()

        binding.continueButton.setOnClickListener {
            saveVitals()
        }
    }

    private fun setupDropdowns() {
        val activityLevels = arrayOf(
            "Low",
            "Moderate",
            "High"
        )

        binding.activityLevelInput.setAdapter(
            ArrayAdapter(
                this,
                android.R.layout.simple_dropdown_item_1line,
                activityLevels
            )
        )

        val yesNo = arrayOf(
            "No",
            "Yes"
        )

        binding.tobaccoInput.setAdapter(
            ArrayAdapter(
                this,
                android.R.layout.simple_dropdown_item_1line,
                yesNo
            )
        )

        binding.alcoholInput.setAdapter(
            ArrayAdapter(
                this,
                android.R.layout.simple_dropdown_item_1line,
                yesNo
            )
        )

        binding.activityLevelInput.setOnClickListener {
            binding.activityLevelInput.showDropDown()
        }

        binding.tobaccoInput.setOnClickListener {
            binding.tobaccoInput.showDropDown()
        }

        binding.alcoholInput.setOnClickListener {
            binding.alcoholInput.showDropDown()
        }
    }

    private fun saveVitals() {
        val heartRateText = binding.heartRateInput.text.toString().trim()
        val systolicText = binding.systolicInput.text.toString().trim()
        val diastolicText = binding.diastolicInput.text.toString().trim()
        val spo2Text = binding.spo2Input.text.toString().trim()
        val temperatureText = binding.temperatureInput.text.toString().trim()
        val activity = binding.activityLevelInput.text.toString().trim()
        val tobacco = binding.tobaccoInput.text.toString().trim()
        val alcohol = binding.alcoholInput.text.toString().trim()

        if (
            heartRateText.isEmpty() ||
            systolicText.isEmpty() ||
            diastolicText.isEmpty() ||
            spo2Text.isEmpty() ||
            temperatureText.isEmpty() ||
            activity.isEmpty() ||
            tobacco.isEmpty() ||
            alcohol.isEmpty()
        ) {
            Toast.makeText(
                this,
                "Please complete all vital information",
                Toast.LENGTH_SHORT
            ).show()
            return
        }

        val heartRate = heartRateText.toDoubleOrNull()
        val systolic = systolicText.toDoubleOrNull()
        val diastolic = diastolicText.toDoubleOrNull()
        val spo2 = spo2Text.toDoubleOrNull()
        val temperature = temperatureText.toDoubleOrNull()

        if (
            heartRate == null ||
            systolic == null ||
            diastolic == null ||
            spo2 == null ||
            temperature == null
        ) {
            Toast.makeText(
                this,
                "Please enter valid numeric values",
                Toast.LENGTH_SHORT
            ).show()
            return
        }

        if (heartRate !in 30.0..220.0) {
            Toast.makeText(
                this,
                "Please enter a valid heart rate",
                Toast.LENGTH_SHORT
            ).show()
            return
        }

        if (systolic !in 70.0..250.0) {
            Toast.makeText(
                this,
                "Please enter a valid systolic blood pressure",
                Toast.LENGTH_SHORT
            ).show()
            return
        }

        if (diastolic !in 40.0..150.0) {
            Toast.makeText(
                this,
                "Please enter a valid diastolic blood pressure",
                Toast.LENGTH_SHORT
            ).show()
            return
        }

        if (spo2 !in 70.0..100.0) {
            Toast.makeText(
                this,
                "SpO₂ must be between 70% and 100%",
                Toast.LENGTH_SHORT
            ).show()
            return
        }

        if (temperature !in 30.0..45.0) {
            Toast.makeText(
                this,
                "Please enter a valid body temperature between 30°C and 45°C",
                Toast.LENGTH_SHORT
            ).show()
            return
        }

        CheckupStateRepository.vitals = mapOf(
            "heart_rate" to heartRate,
            "systolic_bp" to systolic,
            "diastolic_bp" to diastolic,
            "spo2" to spo2,
            "temperature" to temperature,
            "activity_level" to when (activity) {
                "Low" -> 0
                "Moderate" -> 1
                else -> 2
            },
            "tobacco" to if (tobacco == "Yes") 1 else 0,
            "alcohol" to if (alcohol == "Yes") 1 else 0
        )

        startActivity(
            Intent(
                this,
                ImageInputActivity::class.java
            )
        )

        finish()
    }
}