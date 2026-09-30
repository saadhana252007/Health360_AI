package com.example.health360ai.ui.history

import com.example.health360ai.data.model.CheckupSummary
import com.example.health360ai.data.supabase.supabase
import io.github.jan.supabase.auth.auth
import io.github.jan.supabase.postgrest.from
import io.github.jan.supabase.postgrest.query.Order

class HistoryRepository {

    suspend fun getCheckupHistory(userId: String): List<CheckupSummary> {
        return supabase
            .from("checkups")
            .select {
                filter {
                    eq("user_id", userId)
                }
                order(
                    column = "created_at",
                    order = Order.DESCENDING
                )
            }
            .decodeList<CheckupSummary>()
    }
}