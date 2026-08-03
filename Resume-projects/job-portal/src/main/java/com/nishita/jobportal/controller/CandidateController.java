package com.nishita.jobportal.controller;
import com.nishita.jobportal.dto.ApplicationDtos.*;
import com.nishita.jobportal.dto.ProfileDtos.*;
import com.nishita.jobportal.entity.UserAccount;
import com.nishita.jobportal.service.*;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.http.*;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
@RestController @RequestMapping("/api/candidate") @PreAuthorize("hasRole('CANDIDATE')") public class CandidateController{
 private final CurrentUserService current; private final ProfileService profiles; private final ApplicationService applications;
 public CandidateController(CurrentUserService c,ProfileService p,ApplicationService a){current=c;profiles=p;applications=a;}
 @GetMapping("/profile") ProfileResponse profile(Authentication a){return profiles.get(current.require(a));}
 @PutMapping("/profile") ProfileResponse update(@Valid @RequestBody ProfileRequest r,Authentication a){return profiles.update(current.require(a),r);}
 @PostMapping(value="/resume",consumes=MediaType.MULTIPART_FORM_DATA_VALUE) ProfileResponse resume(@RequestPart MultipartFile file,Authentication a){return profiles.resume(current.require(a),file);}
 @PostMapping("/applications") ResponseEntity<ApplicationResponse> apply(@Valid @RequestBody ApplyRequest r,Authentication a){return ResponseEntity.status(201).body(applications.apply(r,current.require(a)));}
 @GetMapping("/applications") Page<ApplicationResponse> applications(@RequestParam(defaultValue="0") int page,@RequestParam(defaultValue="20") int size,Authentication a){return applications.candidate(current.require(a),page,size);}
}
