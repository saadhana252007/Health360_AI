package com.example.health360ai.ui.image

import android.net.Uri
import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.example.health360ai.data.repository.CheckupResultRepository
import com.example.health360ai.data.repository.CheckupStateRepository
import com.example.health360ai.databinding.ActivityImageInputBinding
import com.example.health360ai.ui.checkup.CheckupSubmitState
import com.example.health360ai.ui.checkup.CheckupSubmitViewModel
import com.example.health360ai.ui.result.ResultActivity
import kotlinx.coroutines.launch
import android.content.Intent
import androidx.core.content.FileProvider
import java.io.File

class ImageInputActivity : AppCompatActivity() {

    private lateinit var binding: ActivityImageInputBinding

    private val viewModel: CheckupSubmitViewModel by viewModels()

    private var selectedImageUri: Uri? = null
    private var cameraImageUri: Uri? = null

    private val galleryLauncher =
        registerForActivityResult(
            ActivityResultContracts.GetContent()
        ) { uri ->

            if (uri != null) {
                selectedImageUri = uri

                binding.imagePreview.setImageURI(uri)
                binding.imagePreview.alpha = 1f
            }
        }

    private val cameraLauncher =
        registerForActivityResult(
            ActivityResultContracts.TakePicture()
        ) { success ->

            val uri = cameraImageUri

            if (success && uri != null) {
                selectedImageUri = uri

                binding.imagePreview.setImageURI(uri)
                binding.imagePreview.alpha = 1f
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityImageInputBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupImageType()
        setupButtons()
        observeSubmission()
    }

    private fun setupImageType() {

        val types = arrayOf(
            "Skin",
            "Oral",
            "Wound"
        )

        val adapter = ArrayAdapter(
            this,
            android.R.layout.simple_dropdown_item_1line,
            types
        )

        binding.imageTypeInput.setAdapter(adapter)

        binding.imageTypeInput.setOnClickListener {
            binding.imageTypeInput.showDropDown()
        }
    }

    private fun setupButtons() {

        binding.galleryButton.setOnClickListener {
            galleryLauncher.launch("image/*")
        }

        binding.cameraButton.setOnClickListener {
            openCamera()
        }

        binding.skipImageButton.setOnClickListener {
            skipImage()
        }

        binding.continueButton.setOnClickListener {
            continueToSubmission()
        }
    }
    private fun skipImage() {

        selectedImageUri = null
        cameraImageUri = null

        CheckupStateRepository.imageUri = null
        CheckupStateRepository.imageType = null

        binding.skipImageButton.isEnabled = false
        binding.continueButton.isEnabled = false

        Toast.makeText(
            this,
            "Continuing without image analysis...",
            Toast.LENGTH_SHORT
        ).show()

        viewModel.submitCheckup()
    }

    private fun openCamera() {

        val imageFile = File.createTempFile(
            "health360_",
            ".jpg",
            cacheDir
        )

        val uri = FileProvider.getUriForFile(
            this,
            "${packageName}.fileprovider",
            imageFile
        )

        cameraImageUri = uri

        cameraLauncher.launch(uri)
    }

    private fun continueToSubmission() {

        val imageType =
            binding.imageTypeInput.text
                .toString()
                .trim()

        val imageUri = selectedImageUri

        if (imageType.isEmpty()) {

            Toast.makeText(
                this,
                "Select an image type",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        if (imageUri == null) {

            Toast.makeText(
                this,
                "Select or capture an image",
                Toast.LENGTH_SHORT
            ).show()

            return
        }

        CheckupStateRepository.imageUri = imageUri
        CheckupStateRepository.imageType =
            imageType.lowercase()

        binding.continueButton.isEnabled = false

        Toast.makeText(
            this,
            "Analyzing your checkup...",
            Toast.LENGTH_SHORT
        ).show()

        viewModel.submitCheckup()
    }

    private fun observeSubmission() {

        lifecycleScope.launch {

            repeatOnLifecycle(Lifecycle.State.STARTED) {

                viewModel.state.collect { state ->

                    when (state) {

                        is CheckupSubmitState.Idle -> {
                        }

                        is CheckupSubmitState.Loading -> {

                            binding.continueButton.isEnabled = false
                        }

                        is CheckupSubmitState.Success -> {

                            binding.continueButton.isEnabled = true

                            CheckupResultRepository.result =
                                state.response

                            startActivity(
                                Intent(
                                    this@ImageInputActivity,
                                    ResultActivity::class.java
                                )
                            )

                            finish()
                        }

                        is CheckupSubmitState.Error -> {

                            binding.continueButton.isEnabled = true

                            Toast.makeText(
                                this@ImageInputActivity,
                                state.message,
                                Toast.LENGTH_LONG
                            ).show()
                        }
                    }
                }
            }
        }
    }
}