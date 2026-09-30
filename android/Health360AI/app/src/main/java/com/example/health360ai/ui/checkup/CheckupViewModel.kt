package com.example.health360ai.ui.checkup

import android.net.Uri
import androidx.lifecycle.ViewModel
import com.example.health360ai.data.model.Symptom
import com.example.health360ai.data.model.Profile
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class CheckupViewModel : ViewModel() {

    private val _patient = MutableStateFlow<Profile?>(null)
    val patient: StateFlow<Profile?> = _patient

    private val _vitals = MutableStateFlow<Map<String, Any>>(emptyMap())
    val vitals: StateFlow<Map<String, Any>> = _vitals

    private val _symptoms = MutableStateFlow<Symptom?>(null)
    val symptoms: StateFlow<Symptom?> = _symptoms

    private val _imageUri = MutableStateFlow<Uri?>(null)
    val imageUri: StateFlow<Uri?> = _imageUri

    private val _imageType = MutableStateFlow<String?>(null)
    val imageType: StateFlow<String?> = _imageType

    fun setPatient(profile: Profile) {
        _patient.value = profile
    }

    fun setVitals(vitals: Map<String, Any>) {
        _vitals.value = vitals
    }

    fun setSymptoms(symptoms: Symptom) {
        _symptoms.value = symptoms
    }

    fun setImage(uri: Uri, type: String) {
        _imageUri.value = uri
        _imageType.value = type
    }

    fun clearCheckup() {
        _patient.value = null
        _vitals.value = emptyMap()
        _symptoms.value = null
        _imageUri.value = null
        _imageType.value = null
    }
}