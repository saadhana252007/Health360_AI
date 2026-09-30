package com.example.health360ai.ui.patient

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.health360ai.data.model.Profile
import com.example.health360ai.data.repository.ProfileRepository
import com.example.health360ai.data.supabase.supabase
import io.github.jan.supabase.auth.auth
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class PatientInformationViewModel : ViewModel() {

    private val repository = ProfileRepository()

    private val _profile = MutableStateFlow<Profile?>(null)
    val profile: StateFlow<Profile?> = _profile

    private val _loading = MutableStateFlow(false)
    val loading: StateFlow<Boolean> = _loading

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error

    private val _updateSuccess = MutableStateFlow(false)
    val updateSuccess: StateFlow<Boolean> = _updateSuccess

    fun loadProfile() {
        val userId = supabase.auth.currentUserOrNull()?.id

        if (userId == null) {
            _error.value = "User session not found"
            return
        }

        viewModelScope.launch {
            _loading.value = true
            _error.value = null

            try {
                _profile.value = repository.getProfile(userId)
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to load profile"
            } finally {
                _loading.value = false
            }
        }
    }

    fun updateProfile(profile: Profile) {
        viewModelScope.launch {
            _loading.value = true
            _error.value = null
            _updateSuccess.value = false

            try {
                repository.updateProfile(profile)
                _profile.value = profile
                _updateSuccess.value = true
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to update profile"
            } finally {
                _loading.value = false
            }
        }
    }

    fun resetUpdateSuccess() {
        _updateSuccess.value = false
    }
}