import 'package:flutter/material.dart';

void main() {
  runApp(const DogBCSApp());
}

class DogBCSApp extends StatelessWidget {
  const DogBCSApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Dog Body Condition Analyzer',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF00796B),
          primary: const Color(0xFF00796B),
          surface: Colors.white,
        ),
        scaffoldBackgroundColor: const Color(0xFFF8FAFC),
        cardTheme: CardTheme(
          elevation: 2,
          shadowColor: Colors.black.withOpacity(0.1),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          color: Colors.white,
        ),
      ),
      home: const DogBCSAnalyzerScreen(),
    );
  }
}

class DogBCSAnalyzerScreen extends StatefulWidget {
  const DogBCSAnalyzerScreen({super.key});

  @override
  State<DogBCSAnalyzerScreen> createState() => _DogBCSAnalyzerScreenState();
}

class _DogBCSAnalyzerScreenState extends State<DogBCSAnalyzerScreen> with SingleTickerProviderStateMixin {
  bool _isAnalyzing = false;
  bool _showResult = false;
  bool _hasImage = false; // Mock image state
  
  // Mock result data
  final String _prediction = "Healthy";
  final double _confidence = 0.87;

  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );
    _fadeAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _analyzeCondition() {
    setState(() {
      _isAnalyzing = true;
      _showResult = false;
    });

    // Simulate analysis delay
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        setState(() {
          _isAnalyzing = false;
          _showResult = true;
          _animationController.forward(from: 0);
        });
      }
    });
  }

  void _reset() {
    setState(() {
      _showResult = false;
      _hasImage = false;
      _animationController.reset();
    });
  }

  Color _getResultColor(String condition) {
    switch (condition) {
      case 'Underweight':
        return Colors.amber; // Yellow/Amber
      case 'Healthy':
        return Colors.green; // Green
      case 'Overweight':
        return Colors.red; // Red
      default:
        return Colors.grey;
    }
  }

  String _getSuggestionText(String condition) {
    switch (condition) {
      case 'Underweight':
        return "Dog may require better nutrition";
      case 'Healthy':
        return "Dog body condition is ideal";
      case 'Overweight':
        return "Dog may benefit from diet & exercise";
      default:
        return "";
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Dog Body Condition Analyzer',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        backgroundColor: Colors.white,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 1. Image Upload Section
              _buildImageSection(),
              
              const SizedBox(height: 24),

              // 2. Analyze Button
              _buildAnalyzeButton(),
              
              const SizedBox(height: 32),

              // 3. Result Display Card
              if (_isAnalyzing)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(40.0),
                    child: CircularProgressIndicator(),
                  ),
                ),

              if (_showResult)
                FadeTransition(
                  opacity: _fadeAnimation,
                  child: _buildResultCard(),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildImageSection() {
    return Card(
      child: Container(
        height: 300,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          color: Colors.grey.shade50,
        ),
        child: !_hasImage
            ? Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.cloud_upload_outlined,
                    size: 64,
                    color: Colors.grey.shade400,
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    "Upload dog image",
                    style: TextStyle(
                      fontSize: 18,
                      color: Colors.grey,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: 32),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      _UploadOption(
                        icon: Icons.camera_alt_rounded,
                        label: "Camera",
                        onTap: () => setState(() => _hasImage = true),
                      ),
                      const SizedBox(width: 40),
                      _UploadOption(
                        icon: Icons.photo_library_rounded,
                        label: "Gallery",
                        onTap: () => setState(() => _hasImage = true),
                      ),
                    ],
                  ),
                ],
              )
            : Stack(
                fit: StackFit.expand,
                children: [
                  ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: Container(
                      color: Colors.grey.shade200,
                      child: const Center(
                        child: Icon(Icons.pets, size: 80, color: Colors.white),
                      ),
                    ),
                  ),
                  Positioned(
                    top: 12,
                    right: 12,
                    child: CircleAvatar(
                      backgroundColor: Colors.black.withOpacity(0.5),
                      child: IconButton(
                        icon: const Icon(Icons.close, color: Colors.white),
                        onPressed: _reset,
                      ),
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  Widget _buildAnalyzeButton() {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: ElevatedButton(
        onPressed: (_hasImage && !_isAnalyzing) ? _analyzeCondition : null,
        style: ElevatedButton.styleFrom(
          backgroundColor: Theme.of(context).colorScheme.primary,
          foregroundColor: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
        child: const Text(
          "Analyze Body Condition",
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

  Widget _buildResultCard() {
    final resultColor = _getResultColor(_prediction);
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            const Text(
              "Predicted Condition",
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _prediction,
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: resultColor,
              ),
            ),
            const SizedBox(height: 32),
            
            // Confidence UI
            const Text(
              "Model Confidence",
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 16),
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  height: 90,
                  width: 90,
                  child: CircularProgressIndicator(
                    value: _confidence,
                    strokeWidth: 10,
                    backgroundColor: Colors.grey.shade100,
                    color: resultColor,
                    strokeCap: StrokeCap.round,
                  ),
                ),
                Text(
                  "${(_confidence * 100).toInt()}%",
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 32),
            
            // Suggestion Text
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              decoration: BoxDecoration(
                color: resultColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                _getSuggestionText(_prediction),
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: resultColor.darken(), // Helper extension or just a darker shade
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _UploadOption extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _UploadOption({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(
          children: [
            CircleAvatar(
              radius: 28,
              backgroundColor: Theme.of(context).colorScheme.primary.withOpacity(0.1),
              child: Icon(icon, color: Theme.of(context).colorScheme.primary),
            ),
            const SizedBox(height: 8),
            Text(
              label,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

extension ColorExtension on Color {
  Color darken([double amount = .1]) {
    assert(amount >= 0 && amount <= 1);
    final hsl = HSLColor.fromColor(this);
    final hslDark = hsl.withLightness((hsl.lightness - amount).clamp(0.0, 1.0));
    return hslDark.toColor();
  }
}
