package com.example.health360ai.ui.profile

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.example.health360ai.BuildConfig
import com.example.health360ai.data.repository.CheckupStateRepository
import com.example.health360ai.data.repository.ProfileRepository
import com.example.health360ai.data.supabase.supabase
import com.example.health360ai.databinding.FragmentProfileBinding
import com.example.health360ai.ui.auth.MainActivity
import com.example.health360ai.ui.patient.PatientInformationActivity
import io.github.jan.supabase.auth.auth
import kotlinx.coroutines.launch
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.text.SimpleDateFormat
import java.util.Locale

class ProfileFragment : Fragment() {

    private var _binding: FragmentProfileBinding? = null
    private val binding get() = _binding!!

    private val repository = ProfileRepository()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentProfileBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(
        view: View,
        savedInstanceState: Bundle?
    ) {
        super.onViewCreated(view, savedInstanceState)

        binding.appVersion.text = "v${BuildConfig.VERSION_NAME}"

        loadProfile()

        binding.editProfileButton.setOnClickListener {
            val intent = Intent(
                requireContext(),
                PatientInformationActivity::class.java
            )

            intent.putExtra(
                PatientInformationActivity.EXTRA_EDIT_FROM_PROFILE,
                true
            )

            startActivity(intent)
        }

        binding.privacyButton.setOnClickListener {
            showPrivacySecurity()
        }

        binding.aboutButton.setOnClickListener {
            showAboutHealth360()
        }

        binding.logoutButton.setOnClickListener {
            showLogoutConfirmation()
        }
    }

    private fun loadProfile() {
        viewLifecycleOwner.lifecycleScope.launch {
            try {
                val user = supabase.auth.currentUserOrNull()

                if (user == null) {
                    Toast.makeText(
                        requireContext(),
                        "User session not found",
                        Toast.LENGTH_SHORT
                    ).show()
                    return@launch
                }

                val email = user.email ?: "Not available"

                binding.profileEmail.text = email
                binding.profileEmailHeader.text = email

                val profile = repository.getProfile(user.id)

                if (profile != null) {
                    val name = profile.full_name

                    binding.profileName.text = name
                    binding.profileFullName.text = name

                    binding.profileDob.text =
                        formatDate(profile.date_of_birth)

                    binding.profileSex.text =
                        profile.sex

                    binding.profileHeight.text =
                        "${formatNumber(profile.height_cm)} cm"

                    binding.profileWeight.text =
                        "${formatNumber(profile.weight_kg)} kg"

                    binding.profileInitial.text =
                        name.trim()
                            .firstOrNull()
                            ?.uppercase()
                            ?: "U"

                    binding.profileCreatedAt.text =
                        formatAccountCreatedDate(profile.created_at)
                } else {
                    binding.profileCreatedAt.text = "Not available"
                }

            } catch (e: Exception) {
                binding.profileCreatedAt.text = "Not available"

                Toast.makeText(
                    requireContext(),
                    "Unable to load profile",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }

    private fun formatDate(date: String): String {
        return try {
            val input = SimpleDateFormat(
                "yyyy-MM-dd",
                Locale.getDefault()
            )

            val output = SimpleDateFormat(
                "MMMM d, yyyy",
                Locale.getDefault()
            )

            output.format(input.parse(date)!!)
        } catch (e: Exception) {
            date
        }
    }

    private fun formatAccountCreatedDate(date: String?): String {
        if (date.isNullOrBlank()) {
            return "Not available"
        }

        return try {
            val instant = Instant.parse(date)

            val formatter = DateTimeFormatter.ofPattern(
                "MMMM d, yyyy",
                Locale.getDefault()
            )

            instant
                .atZone(ZoneId.systemDefault())
                .format(formatter)

        } catch (e: Exception) {
            try {
                val input = SimpleDateFormat(
                    "yyyy-MM-dd",
                    Locale.getDefault()
                )

                val output = SimpleDateFormat(
                    "MMMM d, yyyy",
                    Locale.getDefault()
                )

                output.format(input.parse(date)!!)
            } catch (e: Exception) {
                date
            }
        }
    }

    private fun formatNumber(value: Double): String {
        return if (value % 1.0 == 0.0) {
            value.toInt().toString()
        } else {
            value.toString()
        }
    }

    private fun showLogoutConfirmation() {
        AlertDialog.Builder(requireContext())
            .setTitle("Logout")
            .setMessage(
                "Are you sure you want to logout from your Health360 account?"
            )
            .setNegativeButton("Cancel", null)
            .setPositiveButton("Logout") { _, _ ->
                logout()
            }
            .show()
    }

    private fun showPrivacySecurity() {
        AlertDialog.Builder(requireContext())
            .setTitle("Privacy & Security")
            .setMessage(
                "Your Health360 account is protected using Supabase Authentication. " +
                        "Your personal profile and health checkup information are associated " +
                        "with your account and stored securely.\n\n" +
                        "Health360 AI uses your submitted information to provide the health " +
                        "screening features available in the application.\n\n" +
                        "Health360 AI is an AI-assisted screening tool and does not replace " +
                        "professional medical advice."
            )
            .setPositiveButton("Close", null)
            .show()
    }

    private fun showAboutHealth360() {
        AlertDialog.Builder(requireContext())
            .setTitle("About Health360 AI")
            .setMessage(
                "Health360 AI is a modular AI-powered personal health checkup " +
                        "application.\n\n" +
                        "The application combines patient information, symptoms, and optional " +
                        "image analysis to generate an AI-assisted health assessment.\n\n" +
                        "Health360 AI can analyze different image categories such as skin, " +
                        "oral, and wound images and combines available information through " +
                        "a multimodal AI pipeline.\n\n" +
                        "The results are intended for screening and informational purposes " +
                        "and should not be considered a medical diagnosis."
            )
            .setPositiveButton("Close", null)
            .show()
    }

    private fun logout() {
        viewLifecycleOwner.lifecycleScope.launch {
            try {
                supabase.auth.signOut()
                CheckupStateRepository.clear()

                startActivity(
                    Intent(
                        requireContext(),
                        MainActivity::class.java
                    )
                )

                requireActivity().finishAffinity()

            } catch (e: Exception) {
                Toast.makeText(
                    requireContext(),
                    "Logout failed",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }
    }

    override fun onResume() {
        super.onResume()
        loadProfile()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}