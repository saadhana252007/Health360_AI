package com.example.health360ai.data.repository

import com.example.health360ai.data.model.CheckupDetail
import com.example.health360ai.data.supabase.supabase
import io.github.jan.supabase.postgrest.from

class CheckupDetailRepository {

    suspend fun getCheckup(checkupId: String): CheckupDetail {
        return supabase
            .from("checkups")
            .select {
                filter {
                    eq("id", checkupId)
                }
            }
            .decodeSingle<CheckupDetail>()
    }
}