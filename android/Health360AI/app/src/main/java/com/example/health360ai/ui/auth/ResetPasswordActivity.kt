package com.example.health360ai.ui.auth

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.health360ai.data.supabase.supabase
import io.github.jan.supabase.auth.auth
import kotlinx.coroutines.launch
import io.github.jan.supabase.auth.handleDeeplinks
0
class ResetPasswordActivity : AppCompatActivity() {

    private lateinit var newPasswordInput: EditText
    private lateinit var confirmPasswordInput: EditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        supabase.handleDeeplinks(intent)

        val layout = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 48, 48, 48)
        }

        val title = TextView(this).apply {
            text = "Reset Password"
            textSize = 28f
        }

        val subtitle = TextView(this).apply {
            text = "Enter your new Health360 password."
            textSize = 16f
        }

        newPasswordInput = EditText(this).apply {
            hint = "New password"
            inputType = 129
        }

        confirmPasswordInput = EditText(this).apply {
            hint = "Confirm password"
            inputType = 129
        }

        val resetButton = Button(this).apply {
            text = "Update Password"
        }

        layout.addView(title)
        layout.addView(subtitle)
        layout.addView(newPasswordInput)
        layout.addView(confirmPasswordInput)
        layout.addView(resetButton)

        setContentView(layout)

        resetButton.setOnClickListener {
            updatePassword()
        }
    }

    private fun updatePassword() {
        val password = newPasswordInput.text.toString()
        val confirmPassword = confirmPasswordInput.text.toString()

        if (password.isEmpty()) {
            newPasswordInput.error = "Enter a password"
            return
        }

        if (password.length < 6) {
            newPasswordInput.error = "Password must be at least 6 characters"
            return
        }

        if (password != confirmPassword) {
            confirmPasswordInput.error = "Passwords do not match"
            return
        }

        lifecycleScope.launch {
            try {
                supabase.auth.updateUser {
                    this.password = password
                }

                Toast.makeText(
                    this@ResetPasswordActivity,
                    "Password updated successfully",
                    Toast.LENGTH_LONG
                ).show()

                finish()

            } catch (e: Exception) {
                Toast.makeText(
                    this@ResetPasswordActivity,
                    e.message ?: "Unable to update password",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }
}