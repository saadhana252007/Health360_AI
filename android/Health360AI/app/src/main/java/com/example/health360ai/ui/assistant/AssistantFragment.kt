package com.example.health360ai.ui.assistant

import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.ImageButton
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.ScrollView
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.example.health360ai.R
import com.example.health360ai.data.remote.RetrofitInstance
import com.example.health360ai.data.remote.model.AssistantRequest
import com.example.health360ai.data.supabase.supabase
import com.google.android.material.card.MaterialCardView
import io.github.jan.supabase.auth.auth
import kotlinx.coroutines.launch

class AssistantFragment : Fragment() {

    private var checkupId: String? = null

    private lateinit var messagesContainer: LinearLayout
    private lateinit var chatScrollView: ScrollView
    private lateinit var messageInput: EditText
    private lateinit var sendButton: ImageButton
    private lateinit var progressBar: ProgressBar

    override fun onCreate(
        savedInstanceState: Bundle?
    ) {
        super.onCreate(savedInstanceState)

        checkupId =
            arguments?.getString(
                "checkup_id"
            )
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(
            R.layout.fragment_assistant,
            container,
            false
        )
    }

    override fun onViewCreated(
        view: View,
        savedInstanceState: Bundle?
    ) {
        super.onViewCreated(
            view,
            savedInstanceState
        )

        messagesContainer =
            view.findViewById(
                R.id.messagesContainer
            )

        chatScrollView =
            view.findViewById(
                R.id.chatScrollView
            )

        messageInput =
            view.findViewById(
                R.id.messageInput
            )

        sendButton =
            view.findViewById(
                R.id.sendButton
            )

        progressBar =
            view.findViewById(
                R.id.assistantProgress
            )

        view.findViewById<TextView>(
            R.id.explainChip
        ).setOnClickListener {

            messageInput.setText(
                "Explain my health screening result in simple words."
            )

            sendMessage()
        }

        view.findViewById<TextView>(
            R.id.warningChip
        ).setOnClickListener {

            messageInput.setText(
                "What are my warning signs?"
            )

            sendMessage()
        }

        view.findViewById<TextView>(
            R.id.confidenceChip
        ).setOnClickListener {

            messageInput.setText(
                "What does my confidence and uncertainty mean?"
            )

            sendMessage()
        }

        sendButton.setOnClickListener {
            sendMessage()
        }
    }

    private fun sendMessage() {

        val message =
            messageInput.text
                .toString()
                .trim()

        if (message.isEmpty()) {
            return
        }

        addUserMessage(message)

        messageInput.text.clear()

        progressBar.visibility =
            View.VISIBLE

        sendButton.isEnabled =
            false

        lifecycleScope.launch {

            try {

                val session =
                    supabase.auth.currentSessionOrNull()

                if (session == null) {

                    addAssistantMessage(
                        "Your Health360 session has expired. Please sign in again."
                    )

                    return@launch
                }

                val userId =
                    session.user?.id

                if (userId.isNullOrBlank()) {

                    addAssistantMessage(
                        "I couldn't identify your Health360 account."
                    )

                    return@launch
                }

                val request =
                    AssistantRequest(
                        user_id = userId,
                        message = message,
                        checkup_id = checkupId
                    )

                val response =
                    RetrofitInstance.api.assistantChat(
                        request
                    )

                if (response.status == "completed") {

                    addAssistantMessage(
                        response.message
                    )

                } else {

                    addAssistantMessage(
                        "I couldn't process that request. Please try again."
                    )
                }

            } catch (error: Exception) {

                addAssistantMessage(
                    "Something went wrong while connecting to Health360 AI. Please try again."
                )

            } finally {

                progressBar.visibility =
                    View.GONE

                sendButton.isEnabled =
                    true
            }
        }
    }

    private fun addUserMessage(
        message: String
    ) {

        val textView =
            TextView(requireContext())

        textView.text =
            message

        textView.textSize =
            15f

        textView.setLineSpacing(
            6f,
            1.05f
        )

        textView.setTextIsSelectable(
            true
        )

        textView.setTextColor(
            Color.WHITE
        )

        textView.setPadding(
            28,
            18,
            28,
            18
        )

        textView.setBackgroundColor(
            Color.rgb(
                8,
                124,
                131
            )
        )

        val params =
            LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )

        params.gravity =
            Gravity.END

        params.setMargins(
            70,
            8,
            16,
            8
        )

        messagesContainer.addView(
            textView,
            params
        )

        scrollToBottom()
    }

    private fun addAssistantMessage(
        message: String
    ) {

        val card =
            MaterialCardView(
                requireContext()
            )

        val cardParams =
            LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )

        cardParams.gravity =
            Gravity.START

        cardParams.setMargins(
            16,
            8,
            55,
            8
        )

        card.layoutParams =
            cardParams

        card.radius =
            18f

        card.cardElevation =
            2f

        card.strokeColor =
            Color.parseColor(
                "#B9DDDB"
            )

        card.strokeWidth =
            1

        card.setCardBackgroundColor(
            Color.parseColor(
                "#F0F8F8"
            )
        )

        val textView =
            TextView(requireContext())

        textView.text =
            message

        textView.textSize =
            15f

        textView.setTextColor(
            Color.rgb(
                38,
                60,
                66
            )
        )

        textView.setLineSpacing(
            6f,
            1.05f
        )

        textView.setTextIsSelectable(
            true
        )

        textView.setPadding(
            18,
            14,
            18,
            14
        )

        card.addView(
            textView
        )

        messagesContainer.addView(
            card
        )

        scrollToBottom()
    }

    private fun scrollToBottom() {

        chatScrollView.post {

            chatScrollView.fullScroll(
                View.FOCUS_DOWN
            )
        }
    }
}