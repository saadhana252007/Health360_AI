package com.example.health360ai.ui.home

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.example.health360ai.R
import com.example.health360ai.data.model.CheckupSummary
import com.example.health360ai.data.repository.CheckupRepository
import com.example.health360ai.data.repository.ProfileRepository
import com.example.health360ai.data.supabase.supabase
import com.example.health360ai.databinding.FragmentHomeBinding
import com.example.health360ai.ui.patient.PatientInformationActivity
import com.google.android.material.bottomnavigation.BottomNavigationView
import io.github.jan.supabase.auth.auth
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    private val profileRepository = ProfileRepository()
    private val checkupRepository by lazy {
        CheckupRepository(requireContext())
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(
            inflater,
            container,
            false
        )
        return binding.root
    }

    override fun onViewCreated(
        view: View,
        savedInstanceState: Bundle?
    ) {
        super.onViewCreated(view, savedInstanceState)

        setupButtons()
        loadHomeData()
    }

    private fun setupButtons() {
        binding.startCheckupButton.setOnClickListener {
            startCheckup()
        }

        binding.startFirstCheckupText.setOnClickListener {
            startCheckup()
        }

        binding.recentCheckupCard.setOnClickListener {
            startCheckup()
        }

        binding.askAssistantButton.setOnClickListener {
            openAssistant()
        }

        binding.assistantCard.setOnClickListener {
            openAssistant()
        }

        binding.profileInitial.setOnClickListener {
            openProfile()
        }
    }

    private fun startCheckup() {
        startActivity(
            Intent(
                requireContext(),
                PatientInformationActivity::class.java
            )
        )
    }

    private fun openAssistant() {
        val bottomNavigation =
            requireActivity().findViewById<BottomNavigationView>(
                R.id.bottomNavigation
            )

        bottomNavigation.selectedItemId = R.id.nav_assistant
    }

    private fun openProfile() {
        val bottomNavigation =
            requireActivity().findViewById<BottomNavigationView>(
                R.id.bottomNavigation
            )

        bottomNavigation.selectedItemId = R.id.nav_profile
    }

    private fun loadHomeData() {
        viewLifecycleOwner.lifecycleScope.launch {
            try {
                val user = supabase.auth.currentUserOrNull()

                if (user == null) {
                    return@launch
                }

                loadProfile(user.id)
                loadLatestCheckup(user.id)

            } catch (e: Exception) {
                binding.greetingText.text = getGreeting()
                binding.profileInitial.text = "U"
            }
        }
    }

    private suspend fun loadProfile(userId: String) {
        try {
            val profile =
                profileRepository.getProfile(userId)

            if (profile != null) {
                val name = profile.full_name.trim()

                binding.greetingText.text =
                    if (name.isNotEmpty()) {
                        "${getGreeting()}, $name"
                    } else {
                        getGreeting()
                    }

                binding.profileInitial.text =
                    name.firstOrNull()
                        ?.uppercase()
                        ?: "U"
            }
        } catch (e: Exception) {
            binding.greetingText.text = getGreeting()
            binding.profileInitial.text = "U"
        }
    }

    private suspend fun loadLatestCheckup(userId: String) {
        val checkup =
            checkupRepository.getLatestCheckup(userId)

        if (checkup == null) {
            setInitialEmptyState()
            return
        }

        displayLatestCheckup(checkup)
    }

    private fun displayLatestCheckup(checkup: CheckupSummary) {
        val overallScore =
            checkup.overall_score.coerceIn(0.0, 1.0)

        binding.overallHealthValue.text =
            formatPercentage(overallScore)

        binding.lastCheckupValue.text =
            formatDate(checkup.created_at)

        binding.symptomsOverviewValue.text =
            "Completed"

        binding.riskStatusValue.text =
            checkup.overall_category
                ?.replaceFirstChar {
                    it.uppercase()
                }
                ?: "Screening complete"

        binding.recentCheckupTitle.text =
            "Latest health checkup"

        binding.recentCheckupDescription.text =
            "Completed on ${formatDate(checkup.created_at)}"

        binding.startFirstCheckupText.text =
            "Start another checkup  →"
    }

    private fun setInitialEmptyState() {
        binding.overallHealthValue.text =
            "Not assessed"

        binding.lastCheckupValue.text =
            "No checkups yet"

        binding.symptomsOverviewValue.text =
            "Not recorded"

        binding.riskStatusValue.text =
            "Not assessed"

        binding.recentCheckupTitle.text =
            "No checkups yet"

        binding.recentCheckupDescription.text =
            "Complete your first health checkup to see your results here."

        binding.startFirstCheckupText.text =
            "Start your first checkup  →"
    }

    private fun formatPercentage(value: Double): String {
        return String.format(
            Locale.getDefault(),
            "%.0f%%",
            value * 100
        )
    }

    private fun formatDate(value: String): String {
        return try {
            val input =
                SimpleDateFormat(
                    "yyyy-MM-dd'T'HH:mm:ss",
                    Locale.getDefault()
                )

            val output =
                SimpleDateFormat(
                    "dd MMM yyyy",
                    Locale.getDefault()
                )

            output.format(input.parse(value) ?: Date())
        } catch (e: Exception) {
            value.take(10)
        }
    }

    private fun getGreeting(): String {
        val hour =
            java.util.Calendar
                .getInstance()
                .get(java.util.Calendar.HOUR_OF_DAY)

        return when {
            hour < 12 -> "Good morning"
            hour < 17 -> "Good afternoon"
            else -> "Good evening"
        }
    }

    override fun onResume() {
        super.onResume()
        loadHomeData()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}