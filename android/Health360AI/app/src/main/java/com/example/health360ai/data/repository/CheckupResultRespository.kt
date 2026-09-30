package com.example.health360ai.data.repository

import com.example.health360ai.data.remote.CheckupResponse

object CheckupResultRepository {

    var result: CheckupResponse? = null

    fun clear() {
        result = null
    }
}