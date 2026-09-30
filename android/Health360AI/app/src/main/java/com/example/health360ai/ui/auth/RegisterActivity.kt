package com.example.health360ai.ui.auth

import android.R
import android.app.DatePickerDialog
import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.health360ai.data.supabase.supabase
import com.example.health360ai.databinding.ActivityRegisterBinding
import io.github.jan.supabase.auth.auth
import io.github.jan.supabase.auth.providers.builtin.Email
import io.github.jan.supabase.postgrest.from
import kotlinx.coroutines.launch
import kotlinx.serialization.Serializable
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

@Serializable
data class Profile(
    val id: String,
    val full_name: String,
    val date_of_birth: String,
    val sex: String,
    val height_cm: Double,
    val weight_kg: Double
)

class RegisterActivity : AppCompatActivity() {

    private lateinit var binding: ActivityRegisterBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityRegisterBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupSexDropdown()
        setupDatePicker()

        binding.loginLink.setOnClickListener {
            finish()
        }

        binding.createAccountButton.setOnClickListener {
            register()
        }
    }

    private fun setupSexDropdown() {
        val options = arrayOf("Male", "Female", "Other")

        val adapter = ArrayAdapter(
            this,
            R.layout.simple_dropdown_item_1line,
            options
        )

        binding.sexInput.setAdapter(adapter)
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
                        "yyyy-MM-dd",
                        Locale.getDefault()
                    )

                    binding.dobInput.setText(format.format(selected.time))
                },
                calendar.get(Calendar.YEAR),
                calendar.get(Calendar.MONTH),
                calendar.get(Calendar.DAY_OF_MONTH)
            ).show()
        }
    }

    private fun register() {
        val name = binding.fullNameInput.text.toString().trim()
        val dob = binding.dobInput.text.toString().trim()
        val sex = binding.sexInput.text.toString().trim()
        val heightText = binding.heightInput.text.toString().trim()
        val weightText = binding.weightInput.text.toString().trim()
        val email = binding.registerEmailInput.text.toString().trim()
        val password = binding.registerPasswordInput.text.toString()
        val confirmPassword = binding.confirmPasswordInput.text.toString()

        if (name.isEmpty()) {
            showError("Enter your full name")
            return
        }

        if (dob.isEmpty()) {
            showError("Select your date of birth")
            return
        }

        if (sex.isEmpty()) {
            showError("Select your sex")
            return
        }

        if (heightText.isEmpty()) {
            showError("Enter your height")
            return
        }

        if (weightText.isEmpty()) {
            showError("Enter your weight")
            return
        }

        if (email.isEmpty()) {
            showError("Enter your email")
            return
        }

        if (password.length < 8) {
            showError("Password must contain at least 8 characters")
            return
        }

        if (password != confirmPassword) {
            showError("Passwords do not match")
            return
        }

        if (!binding.termsCheckbox.isChecked) {
            showError("Accept the Terms of Service and Privacy Policy")
            return
        }

        val height = heightText.toDoubleOrNull()
        val weight = weightText.toDoubleOrNull()

        if (height == null || height <= 0) {
            showError("Enter a valid height")
            return
        }

        if (weight == null || weight <= 0) {
            showError("Enter a valid weight")
            return
        }

        binding.createAccountButton.isEnabled = false

        lifecycleScope.launch {
            try {
                supabase.auth.signUpWith(Email) {
                    this.email = email
                    this.password = password
                }

                val user = supabase.auth.currentUserOrNull()

                if (user == null) {
                    showError("Account created. Please verify your email and login.")
                    return@launch
                }

                val profile = Profile(
                    id = user.id,
                    full_name = name,
                    date_of_birth = dob,
                    sex = sex,
                    height_cm = height,
                    weight_kg = weight
                )

                supabase.from("profiles").insert(profile)

                Toast.makeText(
                    this@RegisterActivity,
                    "Account created successfully",
                    Toast.LENGTH_SHORT
                ).show()

                finish()

            } catch (e: Exception) {
                showError(e.message ?: "Registration failed")
            } finally {
                binding.createAccountButton.isEnabled = true
            }
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