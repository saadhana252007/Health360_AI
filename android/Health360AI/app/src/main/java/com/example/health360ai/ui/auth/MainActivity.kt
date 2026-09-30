package com.example.health360ai.ui.auth

import android.content.Intent
import android.os.Bundle
import android.text.InputType
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.health360ai.data.supabase.supabase
import com.example.health360ai.databinding.ActivityMainBinding
import com.example.health360ai.ui.home.HomeActivity
import io.github.jan.supabase.auth.auth
import io.github.jan.supabase.auth.providers.builtin.Email
import io.github.jan.supabase.auth.status.SessionStatus
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            supabase.auth.sessionStatus.collect { status ->

                when (status) {

                    is SessionStatus.Authenticated -> {
                        startActivity(
                            Intent(
                                this@MainActivity,
                                HomeActivity::class.java
                            )
                        )
                        finish()
                        return@collect
                    }

                    is SessionStatus.NotAuthenticated -> {
                        showLoginScreen()
                        return@collect
                    }

                    SessionStatus.Initializing -> {
                    }

                    is SessionStatus.RefreshFailure -> {
                        showLoginScreen()
                        return@collect
                    }
                }
            }
        }
    }

    private fun showLoginScreen() {

        if (::binding.isInitialized) {
            return
        }

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.createAccount.setOnClickListener {
            startActivity(
                Intent(
                    this,
                    RegisterActivity::class.java
                )
            )
        }

        binding.forgotPassword.setOnClickListener {
            showForgotPasswordDialog()
        }

        binding.signInButton.setOnClickListener {
            login()
        }
    }

    private fun showForgotPasswordDialog() {

        val emailInput = EditText(this)

        emailInput.hint = "Enter your email"

        emailInput.inputType =
            InputType.TYPE_CLASS_TEXT or
                    InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS

        val container = FrameLayout(this)

        container.setPadding(
            48,
            0,
            48,
            0
        )

        container.addView(
            emailInput,
            FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.WRAP_CONTENT
            )
        )

        AlertDialog.Builder(this)
            .setTitle("Forgot password?")
            .setMessage(
                "Enter your email and we'll send you a password reset link."
            )
            .setView(container)
            .setNegativeButton(
                "Cancel",
                null
            )
            .setPositiveButton(
                "Send reset link"
            ) { _, _ ->
                sendPasswordReset(
                    emailInput.text
                        .toString()
                        .trim()
                )
            }
            .show()
    }

    private fun sendPasswordReset(email: String) {

        if (email.isEmpty()) {

            Toast.makeText(
                this,
                "Enter your email address",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        lifecycleScope.launch {

            try {

                supabase.auth.resetPasswordForEmail(
                    email = email,
                    redirectUrl = "health360://login/reset"
                )

                Toast.makeText(
                    this@MainActivity,
                    "Password reset link sent. Check your email.",
                    Toast.LENGTH_LONG
                ).show()

            } catch (e: Exception) {

                Toast.makeText(
                    this@MainActivity,
                    e.message ?: "Unable to send reset link",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }

    private fun login() {

        val email =
            binding.emailInput.text
                .toString()
                .trim()

        val password =
            binding.passwordInput.text
                .toString()

        if (email.isEmpty()) {

            binding.emailInput.error =
                "Enter your email"

            return
        }

        if (password.isEmpty()) {

            binding.passwordInput.error =
                "Enter your password"

            return
        }

        binding.signInButton.isEnabled = false

        lifecycleScope.launch {

            try {

                supabase.auth.signInWith(
                    Email
                ) {
                    this.email = email
                    this.password = password
                }

                Toast.makeText(
                    this@MainActivity,
                    "Login successful",
                    Toast.LENGTH_SHORT
                ).show()

                startActivity(
                    Intent(
                        this@MainActivity,
                        HomeActivity::class.java
                    )
                )

                finish()

            } catch (e: Exception) {

                Toast.makeText(
                    this@MainActivity,
                    e.message ?: "Login failed",
                    Toast.LENGTH_LONG
                ).show()

            } finally {

                binding.signInButton.isEnabled = true
            }
        }
    }
}