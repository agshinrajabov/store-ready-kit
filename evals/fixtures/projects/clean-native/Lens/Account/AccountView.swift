import AuthenticationServices
import SwiftUI

struct AccountView: View {
    var body: some View {
        VStack {
            SignInWithAppleButton(.signIn) { request in
                request.requestedScopes = [.email]
            } onCompletion: { _ in }
            Button("Delete account", role: .destructive) { Task { await AccountService.deleteAccount() } }
        }
    }
}

enum AccountService {
    static func signUp() async {}
    static func deleteAccount() async {}
}
