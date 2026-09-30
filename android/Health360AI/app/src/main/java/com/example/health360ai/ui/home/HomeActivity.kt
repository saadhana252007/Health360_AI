package com.example.health360ai.ui.home

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import com.example.health360ai.R
import com.example.health360ai.databinding.ActivityHomeBinding
import com.example.health360ai.ui.assistant.AssistantFragment
import com.example.health360ai.ui.history.HistoryFragment
import com.example.health360ai.ui.profile.ProfileFragment
import android.graphics.Color
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.ViewCompat

class HomeActivity : AppCompatActivity() {

    private lateinit var binding: ActivityHomeBinding

    private val homeFragment = HomeFragment()
    private val historyFragment = HistoryFragment()
    private val assistantFragment = AssistantFragment()
    private val profileFragment = ProfileFragment()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        window.navigationBarColor = Color.WHITE
        window.statusBarColor = Color.TRANSPARENT

        binding = ActivityHomeBinding.inflate(layoutInflater)
        setContentView(binding.root)
        ViewCompat.setOnApplyWindowInsetsListener(binding.bottomNavigation) { view, insets ->
            val systemBars = insets.getInsets(
                WindowInsetsCompat.Type.systemBars()
            )

            view.setPadding(
                view.paddingLeft,
                view.paddingTop,
                view.paddingRight,
                systemBars.bottom
            )

            insets
        }

        setupNavigation()

        if (savedInstanceState == null) {
            showFragment(homeFragment)
        }
    }

    private fun setupNavigation() {
        binding.bottomNavigation.setOnItemSelectedListener { item ->

            when (item.itemId) {
                R.id.nav_home -> {
                    showFragment(homeFragment)
                    true
                }

                R.id.nav_history -> {
                    showFragment(historyFragment)
                    true
                }

                R.id.nav_assistant -> {
                    showFragment(assistantFragment)
                    true
                }

                R.id.nav_profile -> {
                    showFragment(profileFragment)
                    true
                }

                else -> false
            }
        }
    }

    private fun showFragment(fragment: Fragment) {
        supportFragmentManager
            .beginTransaction()
            .replace(R.id.homeFragmentContainer, fragment)
            .commit()
    }
}