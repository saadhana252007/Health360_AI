package com.example.health360ai.ui.auth

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.health360ai.data.supabase.supabase
import com.example.health360ai.databinding.ActivityMainBinding
import io.github.jan.supabase.auth.auth
import io.github.jan.supabase.auth.providers.builtin.Email
import kotlinx.coroutines.launch
import com.example.health360ai.ui.home.HomeActivity

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.createAccount.setOnClickListener {
            startActivity(Intent(this, RegisterActivity::class.java))
        }

        binding.signInButton.setOnClickListener {
            login()
        }
    }

    private fun login() {
        val email = binding.emailInput.text.toString().trim()
        val password = binding.passwordInput.text.toString()

        if (email.isEmpty()) {
            binding.emailInput.error = "Enter your email"
            return
        }

        if (password.isEmpty()) {
            binding.passwordInput.error = "Enter your password"
            return
        }

        binding.signInButton.isEnabled = false

        lifecycleScope.launch {
            try {
                supabase.auth.signInWith(Email) {
                    this.email = email
                    this.password = password
                }

                Toast.makeText(
                    this@MainActivity,
                    "Login successful",
                    Toast.LENGTH_SHORT
                ).show()

                startActivity(Intent(this@MainActivity, HomeActivity::class.java))
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