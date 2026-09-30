package com.example.health360ai.ui.result

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.example.health360ai.data.model.Symptom
import com.example.health360ai.data.remote.Assessment
import com.example.health360ai.data.remote.CheckupResponse
import com.example.health360ai.data.remote.ImageResult
import com.example.health360ai.data.remote.ModelResult
import com.example.health360ai.data.remote.ScreeningInterpretation
import com.example.health360ai.data.remote.UncertaintyResult
import com.example.health360ai.data.repository.CheckupDetailRepository
import com.example.health360ai.data.repository.CheckupResultRepository
import com.example.health360ai.data.repository.CheckupStateRepository
import com.example.health360ai.databinding.ActivityResultBinding
import com.google.gson.Gson
import com.google.gson.JsonObject
import com.google.gson.JsonParser
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.launch
import java.util.Locale

class ResultActivity : AppCompatActivity() {

    private lateinit var binding: ActivityResultBinding
    private var historicalResult = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityResultBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val checkupId = intent.getStringExtra("checkup_id")

        historicalResult = checkupId != null

        if (historicalResult) {
            binding.backHomeButton.text = "Back to History"
        } else {
            binding.backHomeButton.text = "Back to Home"
        }

        if (checkupId != null) {
            loadHistoricalResult(checkupId)
        } else {
            val result = CheckupResultRepository.result

            if (result == null) {
                Toast.makeText(
                    this,
                    "Checkup result not available",
                    Toast.LENGTH_SHORT
                ).show()
                finish()
                return
            }

            displayResult(result)
        }

        binding.backHomeButton.setOnClickListener {
            if (historicalResult) {
                finish()
            } else {
                CheckupResultRepository.clear()
                CheckupStateRepository.clear()

                startActivity(
                    Intent(
                        this,
                        com.example.health360ai.ui.home.HomeActivity::class.java
                    ).apply {
                        flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
                    }
                )

                finish()
            }
        }

        binding.askAiButton.setOnClickListener {

            val intent =
                Intent(
                    this,
                    com.example.health360ai.ui.home.HomeActivity::class.java
                ).apply {

                    putExtra(
                        "open_assistant",
                        true
                    )

                    putExtra(
                        "checkup_id",
                        checkupId
                    )

                    flags =
                        Intent.FLAG_ACTIVITY_CLEAR_TOP or
                                Intent.FLAG_ACTIVITY_SINGLE_TOP
                }

            startActivity(intent)
        }
    }

    private fun loadHistoricalResult(checkupId: String) {
        lifecycleScope.launch {
            try {
                val repository = CheckupDetailRepository()
                val detail = repository.getCheckup(checkupId)

                restoreState(detail)

                val result = buildCheckupResponse(detail)

                displayResult(result)

            } catch (e: Exception) {
                Toast.makeText(
                    this@ResultActivity,
                    e.message ?: "Unable to load checkup result",
                    Toast.LENGTH_LONG
                ).show()

                finish()
            }
        }
    }

    private fun restoreState(
        detail: com.example.health360ai.data.model.CheckupDetail
    ) {
        val gson = Gson()

        val patientJson = detail.patient_data?.toString() ?: "{}"

        val patientMap: Map<String, Any> = gson.fromJson(
            patientJson,
            object : TypeToken<Map<String, Any>>() {}.type
        )

        val symptomsObject = detail.symptoms?.toString()?.let {
            JsonParser.parseString(it).asJsonObject
        } ?: JsonParser.parseString("{}").asJsonObject

        val symptoms = Symptom(
            complaint_type = getStringValue(
                symptomsObject,
                "complaint_type",
                "complaintType"
            ),
            severity = getDoubleValue(
                symptomsObject,
                "severity"
            ),
            duration_days = getDoubleValue(
                symptomsObject,
                "duration_days",
                "durationDays"
            ),
            frequency = getDoubleValue(
                symptomsObject,
                "frequency"
            ),
            progression = getDoubleValue(
                symptomsObject,
                "progression"
            ),
            site = getStringValue(
                symptomsObject,
                "site"
            ),
            character = getDoubleValue(
                symptomsObject,
                "character"
            ),
            trigger = getDoubleValue(
                symptomsObject,
                "trigger"
            ),
            associated_symptoms = getStringList(
                symptomsObject,
                "associated_symptoms",
                "associatedSymptoms"
            ),
            pre_symptoms = getStringList(
                symptomsObject,
                "pre_symptoms",
                "preSymptoms"
            ),
            post_symptoms = getStringList(
                symptomsObject,
                "post_symptoms",
                "postSymptoms"
            )
        )

        val vitals = mutableMapOf<String, Any>()

        patientMap["heart_rate"]?.let {
            vitals["heart_rate"] = it
        }

        patientMap["systolic_bp"]?.let {
            vitals["systolic_bp"] = it
        }

        patientMap["diastolic_bp"]?.let {
            vitals["diastolic_bp"] = it
        }

        patientMap["spo2"]?.let {
            vitals["spo2"] = it
        }

        patientMap["temperature"]?.let {
            vitals["temperature"] = it
        }

        CheckupStateRepository.symptoms = symptoms
        CheckupStateRepository.vitals = vitals
        CheckupStateRepository.imageUri = null
        CheckupStateRepository.imageType = null
    }

    private fun buildCheckupResponse(
        detail: com.example.health360ai.data.model.CheckupDetail
    ): CheckupResponse {

        val gson = Gson()

        val imageResult = detail.image_result?.let {
            gson.fromJson(
                it.toString(),
                ImageResult::class.java
            )
        }

        val symptomResult = detail.symptom_result?.let {
            gson.fromJson(
                it.toString(),
                ModelResult::class.java
            )
        } ?: ModelResult()

        val patientResult = detail.patient_result?.let {
            gson.fromJson(
                it.toString(),
                ModelResult::class.java
            )
        } ?: ModelResult()

        val uncertainty = detail.uncertainty_data?.let {
            gson.fromJson(
                it.toString(),
                UncertaintyResult::class.java
            )
        } ?: UncertaintyResult(
            confidence = detail.confidence ?: detail.overall_score,
            uncertainty = detail.uncertainty ?: 0.0,
            completeness = detail.completeness ?: 0.0
        )

        val screening = detail.screening?.let {
            gson.fromJson(
                it.toString(),
                ScreeningInterpretation::class.java
            )
        } ?: buildHistoricalScreening(
            detail,
            symptomResult,
            patientResult,
            imageResult
        )

        val assessment = Assessment(
            imageType = imageResult?.type,
            finding = imageResult?.prediction?.className,
            confidence = imageResult?.prediction?.confidence,
            probabilities = imageResult?.prediction?.probabilities ?: emptyMap()
        )

        return CheckupResponse(
            status = detail.status,
            assessment = assessment,
            screening = screening,
            imageResult = imageResult,
            symptomResult = symptomResult,
            patientResult = patientResult,
            uncertainty = uncertainty
        )
    }

    private fun buildHistoricalScreening(
        detail: com.example.health360ai.data.model.CheckupDetail,
        symptomResult: ModelResult,
        patientResult: ModelResult,
        imageResult: ImageResult?
    ): ScreeningInterpretation {

        val explanations = mutableListOf<String>()

        if (symptomResult.className != null) {
            explanations.add(
                "Symptom model: ${formatLabel(symptomResult.className)} with ${formatPercentage(symptomResult.confidence)} AI confidence."
            )
        }

        if (patientResult.className != null) {
            explanations.add(
                "Patient-risk model: ${formatLabel(patientResult.className)} with ${formatPercentage(patientResult.confidence)} AI confidence."
            )
        }

        if (imageResult?.prediction?.className != null) {
            explanations.add(
                "Image model: ${formatLabel(imageResult.prediction.className)} with ${formatPercentage(imageResult.prediction.confidence)} AI confidence."
            )
        }

        if (explanations.isEmpty()) {
            explanations.add(
                "The recorded AI model outputs were used as part of this screening."
            )
        }

        val mainConcern =
            imageResult?.prediction?.className
                ?: symptomResult.className
                ?: detail.overall_category
                ?: "Health Screening"

        return ScreeningInterpretation(
            mainConcern = formatLabel(mainConcern),
            overallStatus = "SCREENING_COMPLETED",
            screeningSummary = "AI-assisted health screening completed using the recorded checkup information.",
            triage = "",
            redFlags = emptyList(),
            vitalsInterpretation = "The vital signs recorded during this checkup are shown below for reference.",
            modelExplanations = explanations,
            nextSteps = "Review the screening information and seek professional medical advice if symptoms persist, worsen, or cause concern.",
            overallExplanation = "This page presents the AI-assisted screening outputs recorded during the selected checkup. These outputs are screening results and are not a medical diagnosis."
        )
    }

    private fun displayResult(result: CheckupResponse) {

        val screening = result.screening
        val vitals = CheckupStateRepository.vitals
        val symptoms = CheckupStateRepository.symptoms

        binding.mainConcernValue.text =
            formatOverallStatus(screening.overallStatus)

        binding.screeningSummaryValue.text =
            screening.screeningSummary

        if (screening.triage.isBlank()) {
            binding.triageValue.visibility = View.GONE
        } else {
            binding.triageValue.visibility = View.VISIBLE
            binding.triageValue.text = screening.triage
        }

        binding.symptomFindingValue.text =
            formatSymptomFinding(
                result.symptomResult.className ?: "Not available"
            )

        binding.symptomConfidenceValue.text =
            "AI confidence: ${formatPercentage(result.symptomResult.confidence)}"

        binding.symptomDetailsValue.text =
            if (symptoms != null) {
                buildSymptomDetails(symptoms)
            } else {
                "No symptom details available."
            }

        binding.vitalsInterpretationValue.text =
            screening.vitalsInterpretation

        binding.heartRateValue.text =
            formatVital(vitals["heart_rate"], "bpm")

        binding.bloodPressureValue.text =
            formatBloodPressure(
                vitals["systolic_bp"],
                vitals["diastolic_bp"]
            )

        binding.spo2Value.text =
            formatVital(vitals["spo2"], "%")

        binding.temperatureValue.text =
            formatVital(vitals["temperature"], "°C")

        binding.patientFindingValue.text =
            result.patientResult.className ?: "Not available"

        binding.patientConfidenceValue.text =
            "AI confidence: ${formatPercentage(result.patientResult.confidence)}"

        binding.patientExplanationValue.text =
            screening.modelExplanations.firstOrNull {
                it.startsWith("Patient-risk model:")
            } ?: "The patient-risk model was evaluated separately and contributed to the screening."

        if (screening.redFlags.isEmpty()) {
            binding.redFlagsSection.visibility = View.GONE
        } else {
            binding.redFlagsSection.visibility = View.VISIBLE

            binding.redFlagsValue.text =
                buildString {
                    append("The following warning signs were identified from the information provided:\n\n")
                    screening.redFlags.forEach {
                        append("• ")
                        append(it)
                        append("\n")
                    }
                    append("\nPlease seek prompt medical attention based on these warning signs.")
                }
        }

        val imageResult = result.imageResult

        if (imageResult?.prediction == null) {
            binding.imageResultSection.visibility = View.GONE
        } else {
            binding.imageResultSection.visibility = View.VISIBLE

            binding.imageTypeValue.text =
                imageResult.type ?: "Image"

            binding.imageFindingValue.text =
                imageResult.prediction?.className ?: "Not available"

            binding.imageConfidenceValue.text =
                "AI confidence: ${formatPercentage(imageResult.prediction?.confidence)}"

            binding.imageProbabilitiesValue.text =
                formatProbabilities(
                    imageResult.prediction?.probabilities ?: emptyMap()
                )

            binding.imageExplanationValue.text =
                "The image model classified the uploaded image as ${formatLabel(imageResult.prediction?.className ?: "not available")}. The confidence shown above represents the model's classification confidence."
        }

        displayExplainability(screening)
        displayAssessmentQuality(result)

        binding.disclaimerText.text =
            "Health360 AI provides AI-assisted screening information for informational purposes only. It is not a medical diagnosis or a replacement for professional medical advice."
    }

    private fun displayExplainability(
        screening: ScreeningInterpretation
    ) {
        binding.aiAssessmentValue.text =
            if (screening.modelExplanations.isEmpty()) {
                "The recorded AI outputs were used to generate this screening."
            } else {
                screening.modelExplanations.joinToString("\n\n")
            }

        binding.overallExplanationValue.text =
            screening.overallExplanation

        binding.nextStepsValue.text =
            screening.nextSteps
    }

    private fun displayAssessmentQuality(
        result: CheckupResponse
    ) {
        binding.completenessValue.text =
            formatPercentage(result.uncertainty.completeness)

        binding.uncertaintyValue.text =
            formatDecimal(result.uncertainty.uncertainty)
    }

    private fun formatProbabilities(
        probabilities: Map<String, Double>
    ): String {

        if (probabilities.isEmpty()) {
            return "Class probabilities are not available for this recorded result."
        }

        return probabilities.entries
            .sortedByDescending {
                it.value
            }
            .joinToString("\n") {
                "${formatLabel(it.key)}: ${formatPercentage(it.value)}"
            }
    }

    private fun getStringValue(
        objectValue: JsonObject,
        vararg keys: String
    ): String {

        for (key in keys) {
            if (objectValue.has(key) && !objectValue.get(key).isJsonNull) {
                return try {
                    objectValue.get(key).asString
                } catch (e: Exception) {
                    ""
                }
            }
        }

        return ""
    }

    private fun getDoubleValue(
        objectValue: JsonObject,
        vararg keys: String
    ): Double {

        for (key in keys) {
            if (objectValue.has(key) && !objectValue.get(key).isJsonNull) {
                return try {
                    objectValue.get(key).asDouble
                } catch (e: Exception) {
                    0.0
                }
            }
        }

        return 0.0
    }

    private fun getStringList(
        objectValue: JsonObject,
        vararg keys: String
    ): List<String> {

        for (key in keys) {
            if (objectValue.has(key) && !objectValue.get(key).isJsonNull) {
                return try {
                    objectValue.getAsJsonArray(key).map {
                        it.asString
                    }
                } catch (e: Exception) {
                    emptyList()
                }
            }
        }

        return emptyList()
    }

    private fun formatPercentage(
        value: Double?
    ): String {

        if (value == null) {
            return "—"
        }

        return String.format(
            Locale.US,
            "%.0f%%",
            value * 100
        )
    }

    private fun formatDecimal(
        value: Double
    ): String {

        return String.format(
            Locale.US,
            "%.2f",
            value
        )
    }

    private fun formatVital(
        value: Any?,
        unit: String
    ): String {

        if (value == null) {
            return "—"
        }

        return "$value $unit"
    }

    private fun formatBloodPressure(
        systolic: Any?,
        diastolic: Any?
    ): String {

        if (systolic == null || diastolic == null) {
            return "—"
        }

        return "$systolic/$diastolic mmHg"
    }

    private fun formatOverallStatus(
        status: String
    ): String {

        return status
            .replace("_", " ")
            .lowercase()
            .replaceFirstChar {
                it.uppercase()
            }
    }

    private fun formatSymptomFinding(
        value: String
    ): String {

        return value
            .replace("_", " ")
            .replaceFirstChar {
                it.uppercase()
            }
    }

    private fun formatLabel(
        value: String
    ): String {

        return value
            .replace("_", " ")
            .replaceFirstChar {
                it.uppercase()
            }
    }

    private fun buildSymptomDetails(
        symptoms: Symptom
    ): String {

        return buildString {

            append("Complaint: ")

            append(
                if (symptoms.complaint_type.isBlank()) {
                    "Not available"
                } else {
                    formatLabel(symptoms.complaint_type)
                }
            )

            append("\n")

            append("Severity: ")
            append(symptoms.severity)

            append("\n")

            append("Duration: ")
            append(symptoms.duration_days)
            append(" days")

            append("\n")

            append("Frequency: ")
            append(symptoms.frequency)

            append("\n")

            append("Progression: ")
            append(symptoms.progression)

            append("\n")

            append("Site: ")

            append(
                if (symptoms.site.isBlank()) {
                    "Not available"
                } else {
                    formatLabel(symptoms.site)
                }
            )
        }
    }

}