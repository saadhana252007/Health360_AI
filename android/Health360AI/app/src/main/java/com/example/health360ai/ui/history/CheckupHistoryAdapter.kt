package com.example.health360ai.ui.history

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.example.health360ai.data.model.CheckupSummary
import com.example.health360ai.databinding.ItemCheckupHistoryBinding
import java.text.SimpleDateFormat
import java.util.Locale

class CheckupHistoryAdapter(
    private val onCheckupClick: (CheckupSummary) -> Unit
) : RecyclerView.Adapter<CheckupHistoryAdapter.ViewHolder>() {

    private val items = mutableListOf<CheckupSummary>()

    fun submitList(newItems: List<CheckupSummary>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    inner class ViewHolder(
        private val binding: ItemCheckupHistoryBinding
    ) : RecyclerView.ViewHolder(binding.root) {

        fun bind(item: CheckupSummary) {
            binding.checkupDate.text = formatDate(item.created_at)

            binding.checkupTitle.text =
                item.overall_category ?: "Health Screening"

            binding.checkupStatus.text =
                item.status.replaceFirstChar {
                    it.uppercase()
                }

            binding.checkupSummary.text =
                "AI-assisted health screening completed."

            binding.checkupConfidence.text =
                item.confidence?.let {
                    "AI Confidence ${formatPercentage(it)}"
                } ?: "AI Confidence —"

            binding.checkupCompleteness.text =
                item.completeness?.let {
                    "Completeness ${formatPercentage(it)}"
                } ?: "Completeness —"

            binding.triageContainer.visibility = View.GONE

            binding.checkupImageInfo.text =
                "AI screening result available"

            binding.checkupViewResult.setOnClickListener {
                onCheckupClick(item)
            }

            binding.checkupHistoryCard.setOnClickListener {
                onCheckupClick(item)
            }
        }

        private fun formatPercentage(value: Double): String {
            return "${(value * 100).toInt()}%"
        }

        private fun formatDate(value: String): String {
            return try {
                val input = SimpleDateFormat(
                    "yyyy-MM-dd'T'HH:mm:ss.SSSSSSXXX",
                    Locale.US
                )

                val output = SimpleDateFormat(
                    "dd MMM yyyy",
                    Locale.US
                )

                val date = input.parse(value)

                date?.let {
                    output.format(it)
                } ?: value.take(10)

            } catch (e: Exception) {
                value.take(10)
            }
        }
    }

    override fun onCreateViewHolder(
        parent: ViewGroup,
        viewType: Int
    ): ViewHolder {
        val binding = ItemCheckupHistoryBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )

        return ViewHolder(binding)
    }

    override fun onBindViewHolder(
        holder: ViewHolder,
        position: Int
    ) {
        holder.bind(items[position])
    }

    override fun getItemCount(): Int {
        return items.size
    }
}