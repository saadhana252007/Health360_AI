package com.example.health360ai.ui.symptoms

import androidx.lifecycle.ViewModel
import com.example.health360ai.data.model.Symptom
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class SymptomsViewModel : ViewModel() {

    private val _symptom = MutableStateFlow<Symptom?>(null)
    val symptom: StateFlow<Symptom?> = _symptom

    fun saveSymptom(symptom: Symptom) {
        _symptom.value = symptom
    }
}