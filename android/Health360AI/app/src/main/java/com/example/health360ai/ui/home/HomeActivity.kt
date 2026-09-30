package com.example.health360ai.ui.home

import android.graphics.Color
import android.os.Bundle
import android.view.Window
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.constraintlayout.widget.ConstraintLayout
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.fragment.app.Fragment
import com.example.health360ai.R
import com.example.health360ai.databinding.ActivityHomeBinding
import com.example.health360ai.ui.assistant.AssistantFragment
import com.example.health360ai.ui.history.HistoryFragment
import com.example.health360ai.ui.profile.ProfileFragment

class HomeActivity : AppCompatActivity() {

    private lateinit var binding: ActivityHomeBinding

    private val homeFragment = HomeFragment()
    private val historyFragment = HistoryFragment()
    private var assistantFragment = AssistantFragment()
    private val profileFragment = ProfileFragment()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        WindowCompat.setDecorFitsSystemWindows(window, false)

        window.statusBarColor = Color.WHITE
        window.navigationBarColor = Color.WHITE

        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.Q) {
            window.isNavigationBarContrastEnforced = false
            window.navigationBarDividerColor = Color.WHITE
        }

        WindowCompat.getInsetsController(
            window,
            window.decorView
        ).isAppearanceLightStatusBars = true

        WindowCompat.getInsetsController(
            window,
            window.decorView
        ).isAppearanceLightNavigationBars = true

        binding = ActivityHomeBinding.inflate(layoutInflater)
        setContentView(binding.root)

        ViewCompat.setOnApplyWindowInsetsListener(
            binding.bottomNavigation
        ) { view, insets ->

            val navigationBars = insets.getInsets(
                WindowInsetsCompat.Type.navigationBars()
            )

            val params =
                view.layoutParams as ConstraintLayout.LayoutParams

            params.bottomMargin = navigationBars.bottom

            view.layoutParams = params

            insets
        }

        setupNavigation()

        onBackPressedDispatcher.addCallback(
            this,
            object : OnBackPressedCallback(true) {

                override fun handleOnBackPressed() {

                    if (
                        binding.bottomNavigation.selectedItemId !=
                        R.id.nav_home
                    ) {
                        binding.bottomNavigation.selectedItemId =
                            R.id.nav_home
                    } else {
                        isEnabled = false
                        onBackPressedDispatcher.onBackPressed()
                    }
                }
            }
        )

        if (savedInstanceState == null) {

            val openAssistant =
                intent.getBooleanExtra(
                    "open_assistant",
                    false
                )

            if (openAssistant) {

                val checkupId =
                    intent.getStringExtra(
                        "checkup_id"
                    )

                openAssistantFragment(checkupId)

            } else {

                showFragment(homeFragment)
            }
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
            .replace(
                R.id.homeFragmentContainer,
                fragment
            )
            .commit()
    }

    override fun onNewIntent(intent: android.content.Intent) {

        super.onNewIntent(intent)

        setIntent(intent)

        if (
            intent.getBooleanExtra(
                "open_assistant",
                false
            )
        ) {

            val checkupId =
                intent.getStringExtra(
                    "checkup_id"
                )

            openAssistantFragment(checkupId)
        }
    }

    private fun openAssistantFragment(
        checkupId: String?
    ) {

        assistantFragment =
            AssistantFragment().apply {

                arguments =
                    Bundle().apply {
                        putString(
                            "checkup_id",
                            checkupId
                        )
                    }
            }

        binding.bottomNavigation.selectedItemId =
            R.id.nav_assistant

        showFragment(assistantFragment)
    }
}