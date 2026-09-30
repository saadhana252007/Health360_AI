package com.example.health360ai.ui.patient

import android.app.DatePickerDialog
import android.content.Intent
import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.example.health360ai.data.model.Profile
import com.example.health360ai.data.repository.CheckupStateRepository
import com.example.health360ai.databinding.ActivityPatientInformationBinding
import com.example.health360ai.ui.symptoms.SymptomsActivity
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale
import androidx.appcompat.app.AlertDialog

class PatientInformationActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_EDIT_FROM_PROFILE = "edit_from_profile"
    }

    private lateinit var binding: ActivityPatientInformationBinding
    private val viewModel: PatientInformationViewModel by viewModels()
    private var editFromProfile = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        editFromProfile = intent.getBooleanExtra(
            EXTRA_EDIT_FROM_PROFILE,
            false
        )

        binding = ActivityPatientInformationBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupSexDropdown()
        setupDatePicker()
        setupSaveButton()
        observeViewModel()

        viewModel.loadProfile()
    }

    private fun setupSexDropdown() {
        val options = arrayOf("Male", "Female", "Other")

        val adapter = ArrayAdapter(
            this,
            android.R.layout.simple_dropdown_item_1line,
            options
        )

        binding.sexInput.setAdapter(adapter)

        binding.sexInput.setOnClickListener {
            binding.sexInput.showDropDown()
        }
    }

    private fun setupDatePicker() {
        binding.dobInput.setOnClickListener {
            val calendar = Calendar.getInstance()

            DatePickerDialog(
                this,
                { _, year, month, day ->
                    val selected = Calendar.getInstance()
                    selected.set(year, month, day)

                    val format = SimpleDateFormat(
                        "dd-MM-yyyy",
                        Locale.getDefault()
                    )

                    binding.dobInput.setText(
                        format.format(selected.time)
                    )
                },
                calendar.get(Calendar.YEAR),
                calendar.get(Calendar.MONTH),
                calendar.get(Calendar.DAY_OF_MONTH)
            ).show()
        }
    }

    private fun observeViewModel() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {

                launch {
                    viewModel.profile.collect { profile ->
                        profile ?: return@collect
                        displayProfile(profile)
                    }
                }

                launch {
                    viewModel.error.collect { message ->
                        message ?: return@collect

                        Toast.makeText(
                            this@PatientInformationActivity,
                            message,
                            Toast.LENGTH_LONG
                        ).show()
                    }
                }

                launch {
                    viewModel.loading.collect { loading ->
                        binding.saveContinueButton.isEnabled = !loading
                    }
                }

                launch {
                    viewModel.updateSuccess.collect { success ->
                        if (success) {
                            val updatedProfile = viewModel.profile.value

                            if (updatedProfile != null) {
                                CheckupStateRepository.patient = updatedProfile
                            }

                            viewModel.resetUpdateSuccess()

                            if (editFromProfile) {
                                finish()
                            } else {
                                startActivity(
                                    Intent(
                                        this@PatientInformationActivity,
                                        SymptomsActivity::class.java
                                    )
                                )
                            }
                        }
                    }
                }
            }
        }
    }

    private fun displayProfile(profile: Profile) {
        binding.fullNameInput.setText(profile.full_name)

        binding.dobInput.setText(
            formatDateForDisplay(profile.date_of_birth)
        )

        binding.sexInput.setText(
            profile.sex,
            false
        )

        binding.heightInput.setText(
            profile.height_cm.toString()
        )

        binding.weightInput.setText(
            profile.weight_kg.toString()
        )
    }

    private fun setupSaveButton() {
        binding.saveContinueButton.setOnClickListener {
            saveProfile()
        }
    }

    private fun saveProfile() {
        val name = binding.fullNameInput.text.toString().trim()
        val dobDisplay = binding.dobInput.text.toString().trim()
        val sex = binding.sexInput.text.toString().trim()
        val height = binding.heightInput.text.toString().trim().toDoubleOrNull()
        val weight = binding.weightInput.text.toString().trim().toDoubleOrNull()

        if (name.isEmpty()) {
            showError("Enter your full name")
            return
        }

        if (dobDisplay.isEmpty()) {
            showError("Select your date of birth")
            return
        }

        if (sex.isEmpty()) {
            showError("Select your sex")
            return
        }

        if (height == null || height <= 0) {
            showError("Enter a valid height")
            return
        }

        if (weight == null || weight <= 0) {
            showError("Enter a valid weight")
            return
        }

        val currentProfile = viewModel.profile.value

        if (currentProfile == null) {
            showError("Profile data is not loaded")
            return
        }

        val updatedProfile = currentProfile.copy(
            full_name = name,
            date_of_birth = convertDateToDatabaseFormat(dobDisplay),
            sex = sex,
            height_cm = height,
            weight_kg = weight
        )

        viewModel.updateProfile(updatedProfile)
    }

    private fun formatDateForDisplay(date: String): String {
        return try {
            val input = SimpleDateFormat(
                "yyyy-MM-dd",
                Locale.getDefault()
            )

            val output = SimpleDateFormat(
                "dd-MM-yyyy",
                Locale.getDefault()
            )

            output.format(input.parse(date)!!)
        } catch (e: Exception) {
            date
        }
    }

    private fun convertDateToDatabaseFormat(date: String): String {
        return try {
            val input = SimpleDateFormat(
                "dd-MM-yyyy",
                Locale.getDefault()
            )

            val output = SimpleDateFormat(
                "yyyy-MM-dd",
                Locale.getDefault()
            )

            output.format(input.parse(date)!!)
        } catch (e: Exception) {
            date
        }
    }

    private fun showError(message: String) {
        Toast.makeText(
            this,
            message,
            Toast.LENGTH_LONG
        ).show()
    }
}