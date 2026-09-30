package com.example.health360ai.ui.symptoms

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import com.example.health360ai.data.model.Symptom
import com.example.health360ai.data.repository.CheckupStateRepository
import com.example.health360ai.databinding.ActivitySymptomsBinding
import com.example.health360ai.ui.vitals.VitalsActivity

class SymptomsActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySymptomsBinding
    private lateinit var viewModel: SymptomsViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivitySymptomsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        viewModel = ViewModelProvider(this)[SymptomsViewModel::class.java]

        setupComplaintType()
        setupContinueButton()
    }

    private fun setupComplaintType() {
        binding.complaintTypeGroup.setOnCheckedChangeListener { _, checkedId ->
            hideAllSiteGroups()

            when (checkedId) {
                binding.complaintGeneral.id -> {
                    binding.siteQuestion.text =
                        "Where are you experiencing the symptom?"
                    binding.generalSiteGroup.visibility = View.VISIBLE
                }

                binding.complaintSkin.id -> {
                    binding.siteQuestion.text =
                        "Where is the skin concern?"
                    binding.skinSiteGroup.visibility = View.VISIBLE
                }

                binding.complaintOral.id -> {
                    binding.siteQuestion.text =
                        "Where is the oral concern?"
                    binding.oralSiteGroup.visibility = View.VISIBLE
                }

                binding.complaintWound.id -> {
                    binding.siteQuestion.text =
                        "Where is the wound?"
                    binding.woundSiteGroup.visibility = View.VISIBLE
                }
            }
        }
    }

    private fun hideAllSiteGroups() {
        binding.generalSiteGroup.visibility = View.GONE
        binding.skinSiteGroup.visibility = View.GONE
        binding.oralSiteGroup.visibility = View.GONE
        binding.woundSiteGroup.visibility = View.GONE

        binding.generalSiteGroup.clearCheck()
        binding.skinSiteGroup.clearCheck()
        binding.oralSiteGroup.clearCheck()
        binding.woundSiteGroup.clearCheck()
    }

    private fun setupContinueButton() {
        binding.saveContinueButton.setOnClickListener {
            saveSymptoms()
        }
    }

    private fun saveSymptoms() {
        val severity =
            binding.severityInput.text.toString().trim().toDoubleOrNull()

        val duration =
            binding.durationInput.text.toString().trim().toDoubleOrNull()

        if (severity == null || severity !in 0.0..10.0) {
            showError("Enter a severity between 0 and 10")
            return
        }

        if (duration == null || duration < 0) {
            showError("Enter a valid duration")
            return
        }

        val complaintType = when {
            binding.complaintGeneral.isChecked -> "general"
            binding.complaintSkin.isChecked -> "skin"
            binding.complaintOral.isChecked -> "oral"
            binding.complaintWound.isChecked -> "wound"
            else -> null
        }

        if (complaintType == null) {
            showError("Select the type of concern")
            return
        }

        val frequency = when (binding.frequencyGroup.checkedRadioButtonId) {
            binding.frequencyRarely.id -> 1.0
            binding.frequencyOccasionally.id -> 2.0
            binding.frequencyFrequently.id -> 3.0
            binding.frequencyConstantly.id -> 4.0
            else -> null
        }

        val progression = when (binding.progressionGroup.checkedRadioButtonId) {
            binding.progressionBetter.id -> 0.0
            binding.progressionSame.id -> 1.0
            binding.progressionWorse.id -> 2.0
            else -> null
        }

        val site = getSelectedSite(complaintType)

        val character = when (binding.characterGroup.checkedRadioButtonId) {
            binding.characterSharp.id -> 1.0
            binding.characterDull.id -> 2.0
            binding.characterBurning.id -> 3.0
            binding.characterThrobbing.id -> 4.0
            binding.characterCramping.id -> 5.0
            binding.characterPressure.id -> 6.0
            else -> null
        }

        val selectedTriggers = mutableListOf<String>()

        if (binding.triggerMovement.isChecked) {
            selectedTriggers.add("Movement")
        }

        if (binding.triggerFood.isChecked) {
            selectedTriggers.add("Food")
        }

        if (binding.triggerExercise.isChecked) {
            selectedTriggers.add("Exercise")
        }

        if (binding.triggerStress.isChecked) {
            selectedTriggers.add("Stress")
        }

        if (binding.triggerLight.isChecked) {
            selectedTriggers.add("Light")
        }

        if (binding.triggerNone.isChecked) {
            selectedTriggers.add("Nothing specific")
        }

        val trigger = selectedTriggers.size.toDouble()

        if (frequency == null) {
            showError("Select how often you experience the symptom")
            return
        }

        if (progression == null) {
            showError("Select how the symptom is changing")
            return
        }

        if (site == null) {
            showError("Select the location of the concern")
            return
        }

        if (character == null) {
            showError("Select what the symptom feels like")
            return
        }

        val associatedSymptoms =
            getSelectedSymptoms(binding.associatedSymptomsContainer)

        val preSymptoms =
            getSelectedSymptoms(binding.preSymptomsContainer)

        val postSymptoms =
            getSelectedSymptoms(binding.postSymptomsContainer)

        val symptom = Symptom(
            complaint_type = complaintType,
            severity = severity,
            duration_days = duration,
            frequency = frequency,
            progression = progression,
            site = site,
            character = character,
            trigger = trigger,
            associated_symptoms = associatedSymptoms,
            pre_symptoms = preSymptoms,
            post_symptoms = postSymptoms
        )

        viewModel.saveSymptom(symptom)

        CheckupStateRepository.symptoms = symptom

        Toast.makeText(
            this,
            "Symptoms saved",
            Toast.LENGTH_SHORT
        ).show()

        startActivity(
            Intent(
                this,
                VitalsActivity::class.java
            )
        )
    }

    private fun getSelectedSite(
        complaintType: String
    ): String? {
        return when (complaintType) {
            "general" -> when {
                binding.generalHead.isChecked -> "head"
                binding.generalChest.isChecked -> "chest"
                binding.generalAbdomen.isChecked -> "abdomen"
                binding.generalBack.isChecked -> "back"
                binding.generalArms.isChecked -> "arms"
                binding.generalLegs.isChecked -> "legs"
                binding.generalOther.isChecked -> "other"
                else -> null
            }

            "skin" -> when {
                binding.skinFace.isChecked -> "face"
                binding.skinScalp.isChecked -> "scalp"
                binding.skinNeck.isChecked -> "neck"
                binding.skinChest.isChecked -> "chest"
                binding.skinBack.isChecked -> "back"
                binding.skinArms.isChecked -> "arms"
                binding.skinHands.isChecked -> "hands"
                binding.skinLegs.isChecked -> "legs"
                binding.skinFeet.isChecked -> "feet"
                binding.skinOther.isChecked -> "other"
                else -> null
            }

            "oral" -> when {
                binding.oralTeeth.isChecked -> "teeth"
                binding.oralGums.isChecked -> "gums"
                binding.oralTongue.isChecked -> "tongue"
                binding.oralInnerCheek.isChecked -> "inner_cheek"
                binding.oralLips.isChecked -> "lips"
                binding.oralRoof.isChecked -> "roof_of_mouth"
                binding.oralJaw.isChecked -> "jaw"
                binding.oralThroat.isChecked -> "throat"
                binding.oralMultiple.isChecked -> "multiple_areas"
                binding.oralOther.isChecked -> "other"
                else -> null
            }

            "wound" -> when {
                binding.woundHead.isChecked -> "head"
                binding.woundArm.isChecked -> "arm"
                binding.woundHand.isChecked -> "hand"
                binding.woundChest.isChecked -> "chest"
                binding.woundAbdomen.isChecked -> "abdomen"
                binding.woundBack.isChecked -> "back"
                binding.woundLeg.isChecked -> "leg"
                binding.woundFoot.isChecked -> "foot"
                binding.woundOther.isChecked -> "other"
                else -> null
            }

            else -> null
        }
    }

    private fun getSelectedSymptoms(
        container: android.view.ViewGroup
    ): List<String> {
        val selected = mutableListOf<String>()

        for (i in 0 until container.childCount) {
            val card = container.getChildAt(i)

            if (card is android.view.ViewGroup) {
                for (j in 0 until card.childCount) {
                    val child = card.getChildAt(j)

                    if (child is android.widget.CheckBox && child.isChecked) {
                        selected.add(child.text.toString())
                    }
                }
            }
        }

        return selected
    }

    private fun showError(message: String) {
        Toast.makeText(
            this,
            message,
            Toast.LENGTH_SHORT
        ).show()
    }
}