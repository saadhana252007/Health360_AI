package com.example.health360ai.data.repository

import android.net.Uri
import com.example.health360ai.data.model.Profile
import com.example.health360ai.data.model.Symptom

object CheckupStateRepository {

    var patient: Profile? = null

    var vitals: Map<String, Any> = emptyMap()

    var symptoms: Symptom? = null

    var imageUri: Uri? = null

    var imageType: String? = null

    fun clear() {
        patient = null
        vitals = emptyMap()
        symptoms = null
        imageUri = null
        imageType = null
    }
}