/*
 * Copyright 2018 The TensorFlow Authors. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.example.tensorflowdetect;

import android.app.Activity;
import android.app.AppComponentFactory;
import android.graphics.Bitmap;
import android.graphics.Bitmap.Config;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.Paint.Style;
import android.graphics.RectF;
import android.graphics.Typeface;
import android.media.Image;
import android.net.Uri;
import android.os.Bundle;
import android.os.SystemClock;
import android.os.Trace;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.util.TypedValue;
import android.widget.ImageView;
import android.widget.Toast;


import com.example.tensorflowdetect.env.BorderedText;
import com.example.tensorflowdetect.env.ImageUtils;
import com.example.tensorflowdetect.env.Logger;
import com.example.tensorflowdetect.env.Size;
import com.example.tensorflowdetect.tracking.MultiBoxTracker;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.util.LinkedList;
import java.util.List;
import java.util.Vector;
import java.util.stream.Stream;

/**
 * An activity that uses a TensorFlowMultiBoxDetector and ObjectTracker to detect and then track
 * objects.
 */
public class DetectorActivity extends Activity {

    // Configuration values for the prepackaged SSD model.
    private static final int TF_OD_API_INPUT_SIZE = 300;
    private static final boolean TF_OD_API_IS_QUANTIZED = false;
    private static final String TF_OD_API_MODEL_FILE = "widerdetect.tflite";
    private static final String TF_OD_API_LABELS_FILE = "label_face.txt";

    //Image tools
    private byte[][] yuvBytes = new byte[3][];
    private int[] rgbBytes = null;
    private int yRowStride;
    private Runnable postInferenceCallback;
    private Runnable imageConverter;


    // Which detection model to use: by default uses Tensorflow Object Detection API frozen
    // checkpoints.
    private enum DetectorMode {
        TF_OD_API;
    }

    private static final DetectorMode MODE = DetectorMode.TF_OD_API;

    // Minimum detection confidence to track a detection.
    private static final float MINIMUM_CONFIDENCE_TF_OD_API = 0.1f;

    private static final boolean MAINTAIN_ASPECT = false;

    private static final Size DESIRED_PREVIEW_SIZE = new Size(640, 480);

    private static final boolean SAVE_PREVIEW_BITMAP = false;
    private static final float TEXT_SIZE_DIP = 10;

    private Integer sensorOrientation;

    private Classifier detector;

    private long lastProcessingTimeMs;
    private Bitmap rgbFrameBitmap = null;
    private Bitmap croppedBitmap = null;
    private Bitmap cropCopyBitmap = null;

    Bitmap bitmap;

    private boolean computingDetection = false;

    private long timestamp = 0;

    private Matrix frameToCropTransform;
    private Matrix cropToFrameTransform;

    private MultiBoxTracker tracker;

    private byte[] luminanceCopy;

    private BorderedText borderedText;
    ImageView imageView;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        final float textSizePx =
                TypedValue.applyDimension(
                        TypedValue.COMPLEX_UNIT_DIP, TEXT_SIZE_DIP, getResources().getDisplayMetrics());
        borderedText = new BorderedText(textSizePx);
        imageView = (ImageView)findViewById(R.id.imageView);
        borderedText.setTypeface(Typeface.MONOSPACE);


    }

    public void onStart() {
        super.onStart();
        tracker = new MultiBoxTracker(this);

        int cropSize = TF_OD_API_INPUT_SIZE;

        try {
            detector =
                    TFLiteObjectDetectionAPIModel.create(
                            getAssets(),
                            TF_OD_API_MODEL_FILE,
                            TF_OD_API_LABELS_FILE,
                            TF_OD_API_INPUT_SIZE,
                            TF_OD_API_IS_QUANTIZED);

            cropSize = TF_OD_API_INPUT_SIZE;

            BitmapFactory.Options op = new BitmapFactory.Options();
            op.inPreferredConfig = Config.ARGB_8888;
            bitmap = BitmapFactory.decodeResource(getResources(), R.raw.girlbig, op);
            bitmap.getHeight();


        } catch (final IOException e) {
            Log.wtf("Exception initializing classifier!", e);
            Toast toast =
                    Toast.makeText(
                            getApplicationContext(), "Classifier could not be initialized", Toast.LENGTH_SHORT);
            toast.show();
            finish();
        }


        int previewWidth = bitmap.getWidth();
        int previewHeight = bitmap.getHeight();


        sensorOrientation = 0;
//      LOGGER.i("Camera orientation relative to screen canvas: %d", sensorOrientation);

//      LOGGER.i("Initializing at size %dx%d", previewWidth, previewHeight);
        rgbFrameBitmap = Bitmap.createBitmap(previewWidth, previewHeight, Config.ARGB_8888);
        croppedBitmap = Bitmap.createBitmap(bitmap, 0, 0, cropSize, cropSize);

        frameToCropTransform =
                ImageUtils.getTransformationMatrix(
                        previewWidth, previewHeight,
                        cropSize, cropSize,
                        sensorOrientation, MAINTAIN_ASPECT);

        cropToFrameTransform = new Matrix();
        frameToCropTransform.invert(cropToFrameTransform);
        processImage();

//      trackingOverlay = (OverlayView) findViewById(R.id.tracking_overlay);
//      trackingOverlay.addCallback(
//              new DrawCallback() {
//                  @Override
//                  public void drawCallback(final Canvas canvas) {
//                      tracker.draw(canvas);
//                      if (isDebug()) {
//                          tracker.drawDebug(canvas);
//                      }
//                  }
//              });

//      addCallback(
//              new DrawCallback() {
//                  @Override
//                  public void drawCallback(final Canvas canvas) {
//                      if (!isDebug()) {
//                          return;
//                      }
//                      final Bitmap copy = cropCopyBitmap;
//                      if (copy == null) {
//                          return;
//                      }
//
//                      final int backgroundColor = Color.argb(100, 0, 0, 0);
//                      canvas.drawColor(backgroundColor);
//
//                      final Matrix matrix = new Matrix();
//                      final float scaleFactor = 2;
//                      matrix.postScale(scaleFactor, scaleFactor);
//                      matrix.postTranslate(
//                              canvas.getWidth() - copy.getWidth() * scaleFactor,
//                              canvas.getHeight() - copy.getHeight() * scaleFactor);
//                      canvas.drawBitmap(copy, matrix, new Paint());
//
//                      final Vector<String> lines = new Vector<String>();
//                      if (detector != null) {
//                          final String statString = detector.getStatString();
//                          final String[] statLines = statString.split("\n");
//                          for (final String line : statLines) {
//                              lines.add(line);
//                          }
//                      }
//                      lines.add("");
//
//                      lines.add("Frame: " + previewWidth + "x" + previewHeight);
//                      lines.add("Crop: " + copy.getWidth() + "x" + copy.getHeight());
//                      lines.add("View: " + canvas.getWidth() + "x" + canvas.getHeight());
//                      lines.add("Rotation: " + sensorOrientation);
//                      lines.add("Inference time: " + lastProcessingTimeMs + "ms");
//
//                      borderedText.drawLines(canvas, 10, canvas.getHeight() - 10, lines);
//                  }
//              });
    }

    OverlayView trackingOverlay;


    protected void processImage() {
        ++timestamp;
        final long currTimestamp = timestamp;
//    byte[] originalLuminance = getLuminance();
//    tracker.onFrame(
//        previewWidth,
//        previewHeight,
//        getLuminanceStride(),
//        sensorOrientation,
//        originalLuminance,
//        timestamp);
//    trackingOverlay.postInvalidate();


        Log.i("Message:", "Preparing image " + currTimestamp + " for detection in bg thread.");

        rgbFrameBitmap = bitmap;

//    if (luminanceCopy == null) {
//      luminanceCopy = new byte[originalLuminance.length];
//    }
//    System.arraycopy(originalLuminance, 0, luminanceCopy, 0, originalLuminance.length);
//    readyForNextImage();

        final Canvas canvas = new Canvas(croppedBitmap);
        canvas.drawBitmap(rgbFrameBitmap, frameToCropTransform, null);
        // For examining the actual TF input.
        if (SAVE_PREVIEW_BITMAP) {
            ImageUtils.saveBitmap(croppedBitmap);
        }



                Log.i("Detection Message", "Running detection on image " + currTimestamp);
                final long startTime = SystemClock.uptimeMillis();
                final List<Classifier.Recognition> results = detector.recognizeImage(croppedBitmap);
                lastProcessingTimeMs = SystemClock.uptimeMillis() - startTime;

                cropCopyBitmap = Bitmap.createBitmap(croppedBitmap);
               Canvas canvas1 = new Canvas(cropCopyBitmap);
                final Paint paint = new Paint();
                paint.setColor(Color.RED);
                paint.setStyle(Style.FILL);
                paint.setStrokeWidth(5.0f);

                float minimumConfidence = MINIMUM_CONFIDENCE_TF_OD_API;
                switch (MODE) {
                    case TF_OD_API:
                        minimumConfidence = MINIMUM_CONFIDENCE_TF_OD_API;
                        break;
                }

                final List<Classifier.Recognition> mappedRecognitions = new LinkedList<Classifier.Recognition>();

                for (final Classifier.Recognition result : results) {
                    final RectF location = result.getLocation();
                    if (location != null && result.getConfidence() >= minimumConfidence) {
                        canvas1.drawRect(location, paint);
                        Toast.makeText(getApplicationContext(),location.toString(),Toast.LENGTH_LONG).show();
                        cropToFrameTransform.mapRect(location);
                        result.setLocation(location);
                        mappedRecognitions.add(result);
                        imageView.setImageBitmap(cropCopyBitmap);
                    }
                }

                // tracker.trackResults(mappedRecognitions, luminanceCopy, currTimestamp);
                // trackingOverlay.postInvalidate();

//            computingDetection = false;

    }
}





