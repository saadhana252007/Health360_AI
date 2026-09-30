package com.example.health360ai.ui.checkup

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.health360ai.data.remote.CheckupResponse
import com.example.health360ai.data.repository.CheckupRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

sealed class CheckupSubmitState {
    data object Idle : CheckupSubmitState()
    data object Loading : CheckupSubmitState()
    data class Success(val response: CheckupResponse) : CheckupSubmitState()
    data class Error(val message: String) : CheckupSubmitState()
}

class CheckupSubmitViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = CheckupRepository(application)

    private val _state = MutableStateFlow<CheckupSubmitState>(CheckupSubmitState.Idle)
    val state: StateFlow<CheckupSubmitState> = _state

    fun submitCheckup() {
        viewModelScope.launch {
            _state.value = CheckupSubmitState.Loading

            try {
                val response = repository.submitCheckup()
                _state.value = CheckupSubmitState.Success(response)
            } catch (e: Exception) {
                _state.value = CheckupSubmitState.Error(
                    e.message ?: "Checkup submission failed"
                )
            }
        }
    }
}