package com.example.health360ai.ui.history

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.health360ai.data.supabase.supabase
import com.example.health360ai.databinding.FragmentHistoryBinding
import com.example.health360ai.ui.result.ResultActivity
import io.github.jan.supabase.auth.auth
import kotlinx.coroutines.launch

class HistoryFragment : Fragment() {

    private var _binding: FragmentHistoryBinding? = null
    private val binding get() = _binding!!

    private lateinit var adapter: CheckupHistoryAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHistoryBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        loadHistory()
    }

    private fun setupRecyclerView() {
        adapter = CheckupHistoryAdapter { checkup ->
            openResult(checkup.id)
        }

        binding.historyRecyclerView.layoutManager =
            LinearLayoutManager(requireContext())

        binding.historyRecyclerView.adapter = adapter
    }

    private fun loadHistory() {
        binding.historyProgress.visibility = View.VISIBLE
        binding.historyRecyclerView.visibility = View.GONE
        binding.emptyHistoryLayout.visibility = View.GONE

        viewLifecycleOwner.lifecycleScope.launch {
            try {
                val session = supabase.auth.currentSessionOrNull()

                if (session == null) {
                    showEmptyState(
                        "Login required",
                        "Please log in to view your checkup history."
                    )
                    return@launch
                }

                val userId = session.user?.id

                if (userId == null) {
                    showEmptyState(
                        "Account unavailable",
                        "Your user account could not be found."
                    )
                    return@launch
                }

                val repository = HistoryRepository()
                val history = repository.getCheckupHistory(userId)

                if (history.isEmpty()) {
                    showEmptyState(
                        "No checkups yet",
                        "Complete a health checkup and your results will appear here."
                    )
                } else {
                    binding.historyProgress.visibility = View.GONE
                    binding.emptyHistoryLayout.visibility = View.GONE
                    binding.historyRecyclerView.visibility = View.VISIBLE

                    adapter.submitList(history)
                }

            } catch (e: Exception) {
                showEmptyState(
                    "Unable to load history",
                    e.message ?: "Please try again later."
                )

                Toast.makeText(
                    requireContext(),
                    e.message ?: "Unable to load history",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }

    private fun showEmptyState(
        title: String,
        message: String
    ) {
        binding.historyProgress.visibility = View.GONE
        binding.historyRecyclerView.visibility = View.GONE
        binding.emptyHistoryLayout.visibility = View.VISIBLE

        binding.emptyHistoryTitle.text = title
        binding.emptyHistoryMessage.text = message
    }

    private fun openResult(checkupId: String) {
        val intent = Intent(
            requireContext(),
            ResultActivity::class.java
        )

        intent.putExtra("checkup_id", checkupId)

        startActivity(intent)
    }

    override fun onResume() {
        super.onResume()

        if (_binding != null) {
            loadHistory()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}