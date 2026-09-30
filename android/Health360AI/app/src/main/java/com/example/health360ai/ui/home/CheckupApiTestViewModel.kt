package com.example.health360ai.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.health360ai.data.repository.HealthRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class CheckupApiTestViewModel : ViewModel() {

    private val repository = HealthRepository()

    private val _result = MutableStateFlow<String?>(null)
    val result: StateFlow<String?> = _result

    fun testCheckupApi() {
        viewModelScope.launch {
            try {
                val symptoms = mapOf(
                    "severity" to 7,
                    "duration_days" to 5,
                    "frequency" to 3,
                    "progression" to 1,
                    "site" to 2,
                    "character" to 4,
                    "trigger" to 2,
                    "associated_symptoms" to listOf("nausea"),
                    "pre_symptoms" to emptyList<String>(),
                    "post_symptoms" to listOf("fatigue")
                )

                val patient = mapOf(
                    "age" to 20,
                    "sex" to "Female",
                    "height_cm" to 165.0,
                    "weight_kg" to 60.0
                )

                val response = repository.analyzeCheckup(
                    symptoms = symptoms,
                    patient = patient
                )

                _result.value = response.status
            } catch (e: Exception) {
                _result.value = "ERROR: ${e.message}"
            }
        }
    }
}