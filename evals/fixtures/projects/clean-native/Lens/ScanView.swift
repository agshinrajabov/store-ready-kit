import AVFoundation
import SwiftUI

final class ScanModel: ObservableObject {
    let session = AVCaptureSession()
    func start() {
        guard let device = AVCaptureDevice.default(for: .video) else { return }
        _ = device
        UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: "lastScan")
    }
}
