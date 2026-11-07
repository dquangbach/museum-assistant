class MuseumAsset {
  final String id;
  final String originalFilename;
  final String fileUrl;
  final String reviewStatus;

  const MuseumAsset({
    required this.id,
    required this.originalFilename,
    required this.fileUrl,
    required this.reviewStatus,
  });

  factory MuseumAsset.fromJson(Map<String, dynamic> json) => MuseumAsset(
        id: json['id'] as String,
        originalFilename: json['original_filename'] as String,
        fileUrl: json['file_url'] as String,
        reviewStatus: json['review_status'] as String,
      );
}
