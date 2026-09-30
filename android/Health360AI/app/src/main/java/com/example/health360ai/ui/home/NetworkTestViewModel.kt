package com.example.health360ai.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.health360ai.data.repository.HealthRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class NetworkTestViewModel : ViewModel() {

    private val repository = HealthRepository()

    private val _status = MutableStateFlow<String?>(null)
    val status: StateFlow<String?> = _status

    fun checkBackend() {
        viewModelScope.launch {
            try {
                val response = repository.checkHealth()
                _status.value = response["status"]
            } catch (e: Exception) {
                _status.value = "ERROR: ${e.message}"
            }
        }
    }
}